#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 09:49:50 2020

@author: andyb
"""

# %%
from glob import glob
import pandas as pd


# %%
def translate(translation_path):
    t_paths = glob(translation_path)
    tcga_id2gdc_id = pd.DataFrame()
    for path in t_paths:
        ctype = path.split('/')[-1].split('.')[1]
        tmp = pd.read_csv(path, sep='\t')
        tmp['ctype'] = ctype
        tcga_id2gdc_id = pd.concat([tcga_id2gdc_id, tmp])

    tmp = tcga_id2gdc_id.set_index('cases').to_dict()
    tcga_id2gdc_id = tmp['id']
    tcga_id2ctype = tmp['ctype']
    return tcga_id2gdc_id, tcga_id2ctype


# %%
def get_subsampled_signal(df):
    df = df.loc[:, ['chrom', 'start', 'tcga_signal']]
    df['group'] = df['chrom'].apply(str) + ' ' + (df['start'] // 1e6).apply(str)

    tmp = df.groupby(['group']).agg({'tcga_signal': ['median', 'count']})
    tmp = tmp[tmp[('tcga_signal', 'count')] > 500]

    return tmp.loc[:, ('tcga_signal', 'median')]


# %%
translation_path = \
    '/faststorage/project/reprator/Andrej/reprator/data'\
    '/downloaded/seg.*.translation.tsv'

tcga_id2gdc_id, tcga_id2ctype = translate(translation_path)

# %%
smoothing = '1400'

# %%
signal_path = \
    f'/faststorage/project/reprator/Andrej/reprator/data'\
    f'/dfs_TCGA_S_B/*.{smoothing}.fitted.fth'

paths = glob(signal_path)
print(f'There are {len(paths)} paths.')

# %%
main_df = pd.DataFrame()
labels = pd.Series()
for path in paths:
    # load data
    df = pd.read_feather(path)
    tcga_id = path.split('/')[-1].split('.')[0]
    gdc_id = tcga_id2gdc_id[tcga_id]
    ctype = tcga_id2ctype[tcga_id]
    # check if cor > 0.3
    cor = df.loc[:, ['bw_signal', 'tcga_signal']].corr().iloc[0, 1]
    print(f'{gdc_id}\t{cor}')
    if cor > 0.3:
        # subsample
        subsampled_signal = get_subsampled_signal(df)
        main_df[gdc_id] = subsampled_signal
        labels[gdc_id] = ctype

# %%
main_df = main_df.dropna()
main_df = main_df.T
main_df['labels'] = labels

# %%
print(f'File had {main_df.shape[0]} samples with correlation more than 0.3.')
output_file = '/faststorage/project/reprator/Andrej/reprator2/data/subsampled_old.pkl'
main_df.to_pickle(output_file)
