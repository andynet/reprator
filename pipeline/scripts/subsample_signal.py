#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 10:36:28 2020

@author: andyb
"""

# %%
import pandas as pd
from glob import glob


# %%
def get_subsampled_signal(df):
    df = df.loc[:, ['chr', 'start', 'loess']]
    df['group'] = df['chr'] + ' ' + (df['start'] // 1e6).apply(str)

    tmp = df.groupby(['group']).agg({'loess': ['median', 'count']})
    tmp = tmp[tmp[('loess', 'count')] > 500]

    return tmp.loc[:, ('loess', 'median')]


# %%
# ctype = 'BRCA'
# gdc_id = '1251c29c-8d85-4187-80dd-c459542e3080'
smoothing = '2000'
extreme = '2.0'

# %%
signal_path = f'/faststorage/project/reprator/Andrej/reprator2/data/residuals/*'\
    f'/*/smoothing_{smoothing}/extreme_{extreme}/signal.feather'

paths = glob(signal_path)
print(f'There is {len(paths)} paths.')

# %%
main_df = pd.DataFrame()
labels = pd.Series()
for path in paths:
    # load data
    df = pd.read_feather(path)
    gdc_id = path.split('/')[9]
    ctype = path.split('/')[8]
    # check if cor > 0.3
    cor = df.loc[:, ['rep_timing', 'loess']].corr().iloc[0, 1]
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
output_file = '/faststorage/project/reprator/Andrej/reprator2/data/subsampled.pkl'
main_df.to_pickle(output_file)
