# import pynvml
import os
import yaml
import argparse
import torch
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import adjusted_rand_score

from scipy.spatial import distance
from scipy.stats import spearmanr, pearsonr


def getConfig(yaml_path='default.yaml'):
    parser = argparse.ArgumentParser(
        description='Generic runner for VAE models')
    parser.add_argument('--config',
                        '-c',
                        dest="filename",
                        metavar='FILE',
                        help='path to the config file',
                        default=yaml_path)

    args = parser.parse_args()
    with open(args.filename, 'r') as file:
        try:
            config = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            print(exc)

    return config


def getMinUsedGPU(min_index=0, max_index=6):
    if not torch.cuda.is_available():
        return None
    os.system('nvidia-smi -q -d Memory |grep -A4 GPU|grep Free > memory_gpu')
    memory_gpu = [int(x.split()[2])
                  for x in open('memory_gpu', 'r').readlines()]

    return [int(np.argmax(memory_gpu))]


def correlations(A, B, pc_n=100):
    p = (1 - distance.correlation(A.flatten(), B.flatten()))
    spear = spearmanr(A.flatten(), B.flatten())
    dist_genes = np.zeros(A.shape[0])
    for i in range(A.shape[0]):
        dist_genes[i] = 1 - distance.correlation(A[i], B[i])
    pg = (np.average(dist_genes[np.isfinite(dist_genes)]))
    dist_sample = np.zeros(A.shape[1])
    for i in range(A.shape[1]):
        dist_sample[i] = 1 - distance.correlation(A[:, i], B[:, i])
    ps = (np.average(dist_sample[np.isfinite(dist_sample)]))
    pc_dist = []
    if pc_n > 0:
        u0, s0, vt0 = np.linalg.svd(A)
        u, s, vt = np.linalg.svd(B)
        for i in range(pc_n):
            pc_dist.append(abs(1 - distance.cosine(u0[:, i], u[:, i])))
        pc_dist = np.array(pc_dist)
    return p, spear[0], pg, ps, pc_dist


def compare_distances(A, B, random_samples=[], s=200, pvalues=False):
    if len(random_samples) == 0:
        random_samples = np.zeros(A.shape[1], dtype=np.bool)
        random_samples[:min(s, A.shape[1])] = True
        np.random.shuffle(random_samples)
    dist_x = distance.pdist(A[:, random_samples].T, 'euclidean')
    dist_y = distance.pdist(B[:, random_samples].T, 'euclidean')
    pear = pearsonr(dist_x, dist_y)
    spear = spearmanr(dist_x, dist_y)
    if pvalues:
        return pear, spear
    else:
        return pear[0], spear[0]


def compare_results(A, B):
    results = list(correlations(A, B, 0))[:-1]
    results += list(compare_distances(A, B))
    results += list(compare_distances(A.T, B.T))
    return results


def get_observations(X, Phi, snr=5, return_noise=False):
    # X.shape: (gene, cell)
    noise = np.array([np.random.randn(X.shape[1]) for _ in range(X.shape[0])])
    noise *= np.linalg.norm(X)/np.linalg.norm(noise)/snr
    if return_noise:
        return Phi.dot(X + noise), noise
    else:
        return Phi.dot(X + noise)


def read_phi_gene(path):
    file = open(path, 'r')
    document_load = []
    for line in file.readlines():
        line = line.replace('\n', '').replace(' ', '').split(',')[:-1]
        document_load.append(line)
    file.close()
    
    return document_load
    
