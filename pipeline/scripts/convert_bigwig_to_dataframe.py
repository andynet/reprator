#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 19:14:17 2019

@author: andyb
"""

# %%
import pandas as pd
import numpy as np
import pyBigWig
import argparse

# %%
# args = argparse.Namespace()
# args.feather_file = '/faststorage/project/reprator/Andrej/reprator2/data/signal/LUAD/603e16bf-9b05-49c9-a925-f409626c969a.signal.feather'
# args.bigwig_file = '/faststorage/project/reprator/Andrej/reprator2/data/bigwigs/rep_timing.bw'
# args.output = '/faststorage/project/reprator/Andrej/reprator2/data/bigwigs/rep_timing.feather'

# %%
parser = argparse.ArgumentParser(description="Converting the bigwig to dataframe")
parser.add_argument('--feather_file', required=True)
parser.add_argument('--bigwig_file', required=True)
parser.add_argument('--output', required=True)
args = parser.parse_args()

# %%
feather = pd.read_feather(args.feather_file).loc[:, ['chr', 'start', 'end']]
bigwig = pyBigWig.open(args.bigwig_file)

# %%
feather['rep_timing'] = np.nan

# %%
for r, (chrom, start, end, _) in feather.iterrows():
    try:
        mean = np.nanmean(bigwig.values(chrom, start, end))
    except RuntimeError:
        print(f'RuntimeError on row {r}. Index out of bound in bigwig?')
        mean = np.nan
    except RuntimeWarning:
        print(f'RuntimeWarning on row {r}. All values are nan?')
        mean = np.nan

    if r % 1000 == 0:
        print(f'{r}/{feather.shape[0]} completed', end='\r')

    feather.loc[r, 'rep_timing'] = mean

# %%
feather.to_feather(args.output)
