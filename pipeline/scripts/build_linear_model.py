#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 18:22:58 2019

@author: andyb
"""

# %%
import pandas as pd
import argparse
from sklearn.linear_model import LinearRegression
# import seaborn as sns
# import pyBigWig
import numpy as np
from scipy import stats
import time
import statsmodels.api as sm
# import matplotlib.pyplot as plt
from scipy.stats import zscore

# %%
parser = argparse.ArgumentParser(description='build linear model a smooth')
parser.add_argument('--datafile', required=True)
parser.add_argument('--rep_timing', required=True)
parser.add_argument('--signal', required=True)

args = parser.parse_args()

# %%
# args = argparse.Namespace()
# args.datafile = '/faststorage/project/reprator/Andrej/reprator2/data/signal/LUAD/603e16bf-9b05-49c9-a925-f409626c969a.signal.feather'
# args.rep_timing = '/faststorage/project/reprator/Andrej/reprator2/data/bigwigs/rep_timing.feather'
# args.signal = "/faststorage/project/reprator/Andrej/reprator2/data/residuals/LUAD/603e16bf-9b05-49c9-a925-f409626c969a/4000/signal.feather"

# %%
split = args.signal.split('/')
path = '/'.join(split[0: -2])
smoothing = split[-2]

# %%
# args.lm_stats = '/faststorage/project/reprator/Andrej/reprator2/data/results/LUAD/603e16bf-9b05-49c9-a925-f409626c969a.lm_stats.tsv'
args.lm_stats = f'{path}/{smoothing}/lm_stats.tsv'
# args.final_df = '/faststorage/project/reprator/Andrej/reprator2/data/results/LUAD/603e16bf-9b05-49c9-a925-f409626c969a.feather'
# args.final_df = f'{path}/{smoothing}/final_df.feather'
# args.plot_dir = '/faststorage/project/reprator/Andrej/reprator2/data/results/LUAD/603e16bf-9b05-49c9-a925-f409626c969a_plots'
args.plot_dir = f'{path}/{smoothing}/plots'
# plot for each chromosome

# %%
data = pd.read_feather(args.datafile)
data['rep_timing'] = pd.read_feather(args.rep_timing)['rep_timing']
data_pure = data.query('ideal').dropna()

# %%
# sns.jointplot('segment', 'copy', data_pure, kind="hex")
# data_pure.loc[:, ['copy', 'segment']].describe()

# %% build linear model
lm = LinearRegression()
lm.fit(data_pure.loc[:, ['segment']], data_pure['copy'])
r2 = lm.score(data_pure.loc[:, ["segment"]], data_pure["copy"])

# %%
data_pure['predicted'] = lm.predict(data_pure.loc[:, ["segment"]])
data_pure['residuals'] = data_pure["copy"] - data_pure['predicted']

# %%
# data_pure.loc[:, ['residuals', 'rep_timing']].corr()

# %%

# tmp = data_pure

# %%
# sns.lineplot(tmp['start'], stats.zscore(tmp['residuals']))
# sns.lineplot(tmp['start'], stats.zscore(tmp['rep_timing']))
# sns.lineplot(tmp['start'], stats.zscore(tmp['loess']))

# %% filter based on z score
# extreme = 4
# data_pure['residuals_Z_score'] = zscore(data_pure['residuals'])
# tmp = data_pure[data_pure['residuals_Z_score'] < extreme]
# tmp = tmp[tmp['residuals_Z_score'] > -extreme]
# tmp.shape[0] - data_pure.shape[0]


# %%
data_pure['loess'] = np.nan
data_pure.reset_index(drop=True, inplace=True)

# %%
for i in range(22, 0, -1):
    tmp = data_pure.query(f"chr == 'chr{i}'")
    size = tmp.shape[0]

    start = time.time()
    loess = sm.nonparametric.lowess(stats.zscore(tmp['residuals']), range(size),
                                    frac=float(smoothing) / size)
    print(size, time.time() - start)

    data_pure.iloc[tmp.index, -1] = loess[:, 1]

# %%
data_pure.to_feather(args.signal)

# %%
# plt.ioff()
# for i in range(22, 0, -1):
#     fig, ax = plt.subplots()
#     tmp = data_pure.query(f"chr == 'chr{i}'")
#
#     sns.lineplot(tmp['start'], stats.zscore(tmp['rep_timing']), ax=ax)
#     sns.lineplot(tmp['start'], stats.zscore(tmp['loess']), ax=ax)
#     ax.legend(('rep_time', 'loess'))
#
#     outplot = args.plot_dir + f'/chr{i}.png'
#     fig.savefig(outplot, dpi=300)
#     print(outplot)
#
# %%
correlation = data_pure.loc[:, ['rep_timing', 'loess']].corr().iloc[0, 1]

# %%
with open(args.lm_stats, 'w') as f:
    lines = ['intercept\tslope\tr_squared\tcorr\n',
             f'{lm.intercept_}\t{lm.coef_[0]}\t{r2}\t{correlation}\n']
    f.writelines(lines)
