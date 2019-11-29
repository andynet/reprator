#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 14:51:52 2019

@author: andyb
"""

# %%
import pandas as pd
import numpy as np
import argparse

# %%
# args = argparse.Namespace()
# args.manifest = '/faststorage/project/reprator/Andrej/reprator2/data/manifests/LUAD.filtered.tsv'
# args.segments = '/faststorage/project/reprator/Andrej/reprator2/data/segments/LUAD.seg.txt'
# args.signal = '/faststorage/project/reprator/Andrej/reprator2/data/signal/LUAD/603e16bf-9b05-49c9-a925-f409626c969a.tsv'
# args.sample = '603e16bf-9b05-49c9-a925-f409626c969a'
# args.output = '/faststorage/project/reprator/Andrej/reprator2/data/signal/LUAD/603e16bf-9b05-49c9-a925-f409626c969a.signal.feather'

# %%
parser = argparse.ArgumentParser(description='Add segment values to data.')
parser.add_argument('--manifest', required=True)
parser.add_argument('--segments', required=True)
parser.add_argument('--signal', required=True)
parser.add_argument('--sample', required=True)
parser.add_argument('--output', required=True)
args = parser.parse_args()

# %% load signal
signal = pd.read_csv(args.signal, sep='\t').iloc[:, 1:]
segments = pd.read_csv(args.segments, sep='\t')
manifest = pd.read_csv(args.manifest, sep='\t').loc[:, ['file_id', 'segment_cases']]

# %%
segment_case = manifest.query(f'file_id == "{args.sample}"').iloc[0, 1]
records = segments.query(f'Sample == "{segment_case}"')
print(f'segment case: {segment_case}\tnumber of records: {records.shape[0]}')

# %%
signal['segment'] = np.nan

# %%
for _, (_, chrom, start, end, _, value) in records.iterrows():
    q = f'chr == "chr{chrom}" and start > {start} and end < {end}'
    indices = signal.query(q).index
    signal.iloc[indices, 11] = value

# %%
signal.to_feather(args.output)
