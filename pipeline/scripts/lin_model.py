#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 14:39:31 2019

@author: andyb
"""

# %% libraries
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant
from sklearn.linear_model import LinearRegression
from scipy.stats import zscore
import statsmodels.api as sm
import pandas as pd
import numpy as np
import argparse
import time
# import warnings
# warnings.simplefilter('default')


def permutation_test(s1, s2):
    s2 = s2.copy()
    np.random.shuffle(s2.values)
    return s1.corr(s2)


def check_VIF(df):
    df = add_constant(df)
    vifs = [variance_inflation_factor(df.values, i) for i in range(df.shape[1])]
    result = pd.Series(vifs, index=df.columns)
    return result


# %%
# args = argparse.Namespace()
# args.input_file = \
#     '/faststorage/project/reprator/Andrej/reprator2/data/'\
#     'dataframes/BLCA/006c1498-f327-4fff-8936-7d7cb06639f4_1000.tsv.gz'

# args.log_file = \
#     '/faststorage/project/reprator/Andrej/reprator2/data/'\
#     'dataframes/BLCA/006c1498-f327-4fff-8936-7d7cb06639f4_1000.lm.log'

# args.rep_timing_file = \
#     '/faststorage/project/reprator/Andrej/reprator2/data/'\
#     'bigwigs/rep_timing.feather'

# args.output_file = \
#     '/faststorage/project/reprator/Andrej/reprator2/data/'\
#     'dataframes/BLCA/006c1498-f327-4fff-8936-7d7cb06639f4_1000.residuals.tsv.gz'

# %%
parser = argparse.ArgumentParser(description="builds linear model")
parser.add_argument('--input_file', required=True)
parser.add_argument('--rep_timing_file', required=True)
parser.add_argument('--log_file', required=True)
parser.add_argument('--output_file', required=True)
args = parser.parse_args()

# %%
extreme = 2.0
smoothing = 1400

# %% load, rename and filter
df = pd.read_csv(args.input_file, sep='\t', header=0, index_col=0)
df = (df.dropna()
      .query('Ns == 0 and tumor_coverage != 0 and blood_coverage != 0'))

# %%
df.loc[:, 'z_log_tum_cov'] = zscore(np.log(df['tumor_coverage']))
df.loc[:, 'z_log_bld_cov'] = zscore(np.log(df['blood_coverage']))

df = (df.query(f'-{extreme} < z_log_tum_cov < {extreme}')
      .query(f'-{extreme} < z_log_bld_cov < {extreme}'))

# %%
# print(df.loc[:, 'z_log_tum_cov'].corr(df.loc[:, 'z_log_bld_cov']))
# print(permutation_test(df.loc[:, 'z_log_tum_cov'], df.loc[:, 'z_log_bld_cov']))

# %% filter segment outliers
df.loc[:, 'z_segment'] = zscore(df['segment'])
df = df.query(f'-{extreme} < z_segment < {extreme}')

# %%
lm = LinearRegression()
X = df.loc[:, ["z_segment", "z_log_bld_cov"]]
y = df.loc[:, "z_log_tum_cov"]
lm.fit(X, y)

# %%
df.loc[:, 'predicted'] = lm.predict(X)
df.loc[:, 'residuals'] = df['z_log_tum_cov'] - df['predicted']

# %%
with open(args.log_file, 'w') as f:
    f.write(f'smoothing parameter: {smoothing}\nextreme parameter: {extreme}\n')
    vifs = check_VIF(X)
    for index, value in vifs.iteritems():
        f.write(f'VIF of {index} = {round(value, 4)}\n')

    f.write(
        f'z_log_tum_cov = '
        f'{round(lm.intercept_, 4)} + '
        f'{round(lm.coef_[0], 4)} * z_segment + '
        f'{round(lm.coef_[1], 4)} * z_log_bld_cov\n'
    )
    f.write(
        f'r-squared = {round(lm.score(X, y), 4)}\n'
    )


# %% add rep_timing signal
df.columns = [
    'chr', 'start', 'end', 'Ns', 'tumor_coverage', 'segment',
    'blood_coverage', 'z_log_tum_cov', 'z_log_bld_cov', 'z_segment',
    'predicted', 'residuals'
]
df = df.set_index(['chr', 'start'])

rep_timing = pd.read_feather(args.rep_timing_file)
rep_timing['start'] -= 1
rep_timing = rep_timing.set_index(['chr', 'start'])

df = df.join(rep_timing, lsuffix='_l', rsuffix='_r')
df = df.dropna()

assert (df['end_l'] == df['end_r'] - 1).all()

df = df.drop(columns=['end_l', 'end_r'])
df = df.reset_index()

# %% smooth
df['loess'] = np.nan
for chrom in df['chr'].unique():
    tmp = df.query(f"chr == '{chrom}'")
    size = tmp.shape[0]
    print(chrom, size)

    start = time.time()
    loess = sm.nonparametric.lowess(
        zscore(tmp['residuals']), range(size),
        frac=min(float(smoothing) / size, 1))

    with open(args.log_file, 'a') as f:
        f.write(f'{chrom}\t{size}\t{round(time.time() - start, 2)}\n')

    df.loc[tmp.index, 'loess'] = loess[:, 1]

# %%
df.to_csv(args.output_file, sep='\t', compression='gzip')
