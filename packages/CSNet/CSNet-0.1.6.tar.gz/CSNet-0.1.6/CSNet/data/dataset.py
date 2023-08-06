from torch.utils.data.dataset import random_split, Dataset
from ._utils import DataLoaderX
import pytorch_lightning as pl
import scanpy as sc
import numpy as np
import os
import gc


class h5adDataset(Dataset):
    def __init__(self,
                 data_path: str,
                 isPredict: bool = False):
        self.adata = sc.read_h5ad(data_path)
        if isPredict:
            self.count = self.adata.obsm['measurements']
            self.library = self.adata.obsm['library']
        else:
            self.count = self.adata.layers['counts'].toarray()
            self.library = np.log(self.count.sum(-1)+1)
        self.count = self.count.astype(np.float32)
        self.library = self.library.astype(np.float32)
        self.shape = self.adata.shape

    def __getitem__(self, idx):
        return self.count[idx], self.library[idx]

    def __len__(self):
        return self.adata.shape[0]


class DataLight(pl.LightningDataModule):
    def __init__(self,
                 DIR: str,
                 gpus: list = [0],
                 test_path: str = None,
                 num_workers: int = 4,
                 batch_size: int = 128,
                 isPredict: bool = False,
                 **kwargs):
        super().__init__()
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.DIR = DIR
        self.isPredict = isPredict
        self.gpus = gpus
        self.test_path = os.path.join(
            self.DIR, 'test_M.h5ad') if test_path is None else test_path
        self.prepare_data()

    def prepare_data(self):
        if self.isPredict:
            self.dataset_test = h5adDataset(
                self.test_path, isPredict=self.isPredict)
            self.gene_dim = self.dataset_test.adata.uns['gene_dim']
        else:
            self.dataset_train = h5adDataset(
                os.path.join(self.DIR, 'train.h5ad'),
                self.isPredict)
            self.dataset_val = h5adDataset(
                os.path.join(self.DIR, 'val.h5ad'),
                self.isPredict)
            self.dataset_test = h5adDataset(
                os.path.join(self.DIR, 'test.h5ad'), isPredict=self.isPredict)
            self.gene_dim = self.dataset_train.shape[1]

        gc.collect()

    def train_dataloader(self):
        shape_ = self.dataset_train.shape
        print(f'train_size: {shape_}')
        return DataLoaderX(dataset=self.dataset_train,
                           pin_memory=False,
                           local_rank=int(self.gpus[0]),
                           batch_size=self.batch_size,
                           num_workers=self.num_workers,
                           shuffle=True)

    def val_dataloader(self):
        shape_ = self.dataset_val.shape
        print(f'val_size: {shape_}')
        return DataLoaderX(dataset=self.dataset_val,
                           pin_memory=False,
                           local_rank=int(self.gpus[0]),
                           batch_size=self.batch_size,
                           num_workers=self.num_workers,
                           shuffle=False)

    def test_dataloader(self):
        shape_ = self.dataset_test.shape
        print(f'test_size: {shape_}')
        return DataLoaderX(dataset=self.dataset_test,
                           pin_memory=False,
                           local_rank=int(self.gpus[0]),
                           batch_size=self.batch_size,
                           num_workers=self.num_workers,
                           shuffle=False)


if __name__ == '__main__':
    # python -m CSNet.data.dataset
    import os
    from ..function import getMinUsedGPU
    os.environ['CUDA_LAUNCH_BLOCKING'] = '1'
    DIR = '/data/xizhu/shen/ST/CSNet/data/CSNet'
    gpus = getMinUsedGPU()
    dataLight = DataLight(DIR, gpus)
    train_loader = dataLight.train_dataloader()
    val_loader = dataLight.val_dataloader()
    test_loader = dataLight.test_dataloader()
    iter_ = iter(train_loader)
    batch = next(iter_)
    print(batch)
    x, library = batch
    print(x.shape)
    print(library.shape)
