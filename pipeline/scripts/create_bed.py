#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 11:21:18 2019

@author: andyb
"""

# %%
from Bio import SeqIO
import argparse
import gzip

# %%
parser = argparse.ArgumentParser(description="Creating bed file")
parser.add_argument('--input', required=True)
parser.add_argument('--bin_size', required=True, type=int)
parser.add_argument('--output', required=True)
args = parser.parse_args()

# %%
with gzip.open(args.input, "rt") as in_fd, open(args.output, 'w') as out_fd:
    chromosomes = [f"chr{i}" for i in range(1, 23)]
    records = [record for record in SeqIO.parse(in_fd, 'fasta') if record.id in chromosomes]
    records = sorted(records, key=lambda x: int(x.id[3:]))

    for record in records:
        for i in range(0, len(record.seq), args.bin_size):
            Ns = record.seq[i:i + 1000].count('N')
            out_fd.write(f"{record.id}\t{i}\t{min(i + 1000, len(record.seq))}\t{Ns}\n")

# %%
# [f(x) if condition else g(x) for x in sequence]
# [f(x) for x in sequence if condition]
