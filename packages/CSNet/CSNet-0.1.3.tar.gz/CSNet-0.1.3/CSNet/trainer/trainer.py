import os
import yaml
import torch
import wandb
import numpy as np
import pytorch_lightning as pl
from CSNet.experiment.experiment import ExprLight
from pytorch_lightning.loggers import WandbLogger
from pytorch_lightning.callbacks import EarlyStopping, ModelCheckpoint
from ..function import getMinUsedGPU


class Trainer(object):
    def __init__(self, DIR: str = None, project: str = 'CS', entity: str = 'ustcszq'):
        self.DIR = DIR
        self.project = project
        self.entity = entity

    def wandb_init(self, WANDB_MODE: str, file: str, wandb_use=True):
        if wandb_use:
            os.environ["WANDB_MODE"] = WANDB_MODE
            wandb.init(
                project=self.project,
                entity=self.entity,
                config=os.path.join(self.DIR, file),
                settings=wandb.Settings(start_method='thread')
            )
            config = wandb.config
        else:
            with open(os.path.join(self.DIR, 'predict.yaml')) as f:
                config = yaml.load(f, yaml.SafeLoader)

        torch.manual_seed(config['manual_seed'])
        np.random.seed(config['manual_seed'])
        config['gpus'] = getMinUsedGPU()
        config['DIR'] = self.DIR

        self.config = config

    def experiment_init(self, save_top_k=3, patience=5, mode='min', monitor='val/loss', max_epochs=100, gpus=None, model_path=None, **config):
        experiment = ExprLight(**config)

        wandb_logger = WandbLogger(
            save_dir='wandb'
        )

        early_stopping = EarlyStopping(
            monitor=monitor,
            mode=mode,
            patience=patience
        )

        checkpoint_callback = ModelCheckpoint(
            monitor=monitor,
            dirpath=os.path.join(wandb_logger.experiment.dir, '../checkpoint'),
            filename="{epoch:02d}-{val_loss:.2e}",
            save_top_k=save_top_k,
            mode=mode,
        )

        runner = pl.Trainer(
            strategy='dp',
            precision=16,
            benchmark=True,
            limit_train_batches=1.0,  # 控制数据集读入比例
            limit_val_batches=1.0,
            limit_test_batches=1.0,
            log_every_n_steps=100,
            logger=wandb_logger,
            callbacks=[early_stopping, checkpoint_callback],
            check_val_every_n_epoch=1,
            num_sanity_val_steps=0,
            max_epochs=max_epochs,
            gpus=gpus
        )
        if model_path:
            ckpt = torch.load(model_path)
            experiment.load_state_dict(ckpt['state_dict'])

        self.wandb_logger = wandb_logger
        self.early_stopping = early_stopping
        self.early_stopping = early_stopping
        self.checkpoint_callback = checkpoint_callback
        self.experiment = experiment
        self.runner = runner

    def yaml_write(self, config):
        model_path = self.checkpoint_callback.best_model_path
        config = config.as_dict()
        config['model_path'] = model_path
        config['isPredict'] = True
        config['test_path'] = os.path.join(self.DIR, 'test_M.h5ad')
        with open(os.path.join(self.DIR, 'predict.yaml'), 'w') as f:
            yaml.dump(config, f)
        with open(os.path.join(self.experiment.save_dir, 'predict.yaml'), 'w') as f:
            yaml.dump(config, f)

    def fit(self, WANDB_MODE='offline'):
        self.wandb_init(WANDB_MODE, 'train.yaml', wandb_use=True)
        self.experiment_init(**self.config)
        self.runner.fit(self.experiment)
        self.runner.test(ckpt_path='best')
        self.yaml_write(self.config)
        wandb.finish()

    def test(self):
        self.wandb_init('offline', 'predict.yaml', wandb_use=False)
        assert self.config['model_path'] != None, 'model_path is None'
        self.experiment_init(**self.config)
        self.runner.test(self.experiment)
        wandb.finish()
