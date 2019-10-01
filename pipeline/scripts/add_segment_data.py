#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 13:36:59 2019

@author: andyb
"""


# %% imports
import pandas as pd
import argparse

# %% parsing arguments
parser = argparse.ArgumentParser(description="Adding segment data")
parser.add_argument('--segments', required=True)
parser.add_argument('--gdc_query', required=True)
parser.add_argument('--merged', required=True)
parser.add_argument('--filtered', required=True)
args = parser.parse_args()

# %% load data
query = pd.read_csv(args.gdc_query, sep='\t')

segments = pd.read_csv(args.segments, sep='\t', header=None)
segments.columns = ['segment_cases']

# %% add segment cases to dataframe
query['prefix'] = [x[0:20] for x in query['cases']]
segments['prefix'] = [x[0:20] for x in segments['segment_cases']]

merged = query.merge(segments, on=['prefix'], how='left')

# %% save dataframe
merged.to_csv(args.merged, sep='\t')

# %% filter out missing and non-'Primary solid Tumor' entries
filtered = merged.dropna(axis=1, how='all').dropna(axis=0, how='any')
filtered = filtered[filtered['tissue.definition'] == 'Primary solid Tumor']

# %% save dataframe
filtered.to_csv(args.filtered, sep='\t')
