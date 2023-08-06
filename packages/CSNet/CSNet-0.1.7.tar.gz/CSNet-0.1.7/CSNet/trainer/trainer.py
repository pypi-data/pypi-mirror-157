import sys
import os
from tqdm import tqdm
import yaml
import torch
import wandb
import numpy as np
import pytorch_lightning as pl
from CSNet.experiment.experiment import ExprLight
from pytorch_lightning.loggers import WandbLogger
from pytorch_lightning.callbacks import EarlyStopping, ModelCheckpoint
from ..function import getMinUsedGPU, correlations
import pandas as pd
import wandb


class Trainer(object):
    def __init__(self, DIR: str = None, project: str = 'CS', entity: str = 'ustcszq'):
        self.DIR = DIR
        self.project = project
        self.entity = entity

    def wandb_init(self, WANDB_MODE: str, file: str, wandb_use=True):
        os.environ["WANDB_MODE"] = WANDB_MODE
        if wandb_use:
            self.wandb_run = wandb.init(
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

    def experiment_init(self, save_top_k=3, patience=5, mode='min', monitor='val/loss', max_epochs=100, model_path=None, **config):
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
            precision=32,
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
            gpus=config['gpus'],
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
        self.As = []
        self.scores = []
        self.phi_optimize()
        for i, corr in zip(self.scores.columns, self.best_score.values):
            self.wandb_run.log({'final/'+i: corr})
        wandb.finish()

    def predict(self):
        self.wandb_init('offline', 'predict.yaml', wandb_use=False)
        assert self.config['model_path'] != None, 'model_path is None'
        self.experiment_init(**self.config)
        self.runner.test(self.experiment)
        wandb.finish()

    def phi_test(self, adata, dataloader):
        self.experiment.isPredict = True
        results = []
        for batch in dataloader:
            batch[0] = batch[0].to(self.experiment.device)
            batch[1] = batch[1].to(self.experiment.device)
            result = self.experiment.model.predict(batch)
            results.append(result)
        target = adata.layers['counts'].toarray()
        predict = torch.cat(results).detach().cpu().numpy()
        corrs = list(correlations(target.T, predict.T, 0))[:-1]

        return corrs

    def phi_optimize(self, monitor='cell_pearson'):
        for i in tqdm(range(self.config['phi_times'])):
            with HiddenPrints():
                A = self.experiment.phi_optimize()
                self.As.append(A)
                corrs = self.phi_test(
                    self.experiment.dataset.dataset_val.adata,
                    self.experiment.dataset.val_dataloader())
                self.scores.append(corrs)
                corrs = self.phi_test(
                    self.experiment.dataset.dataset_test.adata,
                    self.experiment.dataset.test_dataloader())
                self.scores[-1] += corrs
        self.result_arrange(monitor)
        self.result_save()

    def result_arrange(self, monitor='cell_pearson'):
        df = pd.DataFrame(self.scores)
        df.columns = ['val_overall_pearson',
                      'val_overall_spearman',
                      'val_gene_pearson',
                      'val_cell_pearson',
                      'test_overall_pearson',
                      'test_overall_spearman',
                      'test_gene_pearson',
                      'test_cell_pearson']
        col = f'val_{monitor}'
        best_index = df[col].argmax()
        self.best_score = df.loc[best_index]
        self.best_A = self.As[best_index]
        self.scores = df
        print('best_score')
        print(df.loc[best_index])

    def result_save(self):
        save_dir = self.experiment.save_dir
        print('save_dir:', save_dir)

        A = self.best_A
        np.save(os.path.join(save_dir, 'phi.npy'), A)
        self.wandb_run.log({'final/sparsity': A.sum()/A.shape[0]/A.shape[1]})
        print('A_sparsity:', A.sum()/A.shape[0]/A.shape[1])

        adata = self.experiment.dataset.dataset_test.adata
        adata.obsm['measurements'] = adata.layers['counts'].dot(A.T)
        adata.obsm['library'] = self.experiment.dataset.dataset_test.library
        adata.write(os.path.join(self.DIR, 'test_M.h5ad'))
        print('Save pseudo measurements')

        filename = open(os.path.join(save_dir, 'phi.txt'), 'w')
        for i in range(len(A)):
            genes = adata.var_names[A[i] > 0].tolist()
            for gene in genes[:-1]:
                filename.write(gene+', ')
            filename.write(genes[-1]+'\n')
        filename.close()
        print('Save genenames of measurements')


class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout
