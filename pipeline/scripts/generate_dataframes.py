#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 13:28:24 2019

@author: andyb
"""

# %%
import pandas as pd
import random
import argparse
import re


def check_data(df):
    start = random.randint(0, 1000)
    print(df.query(f'{start}000 < start < {start+2}000'))


def convert_gdc2tcga(filepath, gdc_id):
    tcga_id = (pd.read_csv(filepath, sep='\t')
               .loc[:, ['id', 'cases']]
               .set_index('id')
               .to_dict()['cases'][gdc_id])

    return tcga_id


def parse_tcga_id(tcga_id):
    # https://docs.gdc.cancer.gov/Encyclopedia/pages/TCGA_Barcode/
    project, tissue_source_site, participant, sample_vial, *_ = tcga_id.split('-')
    return f'{project}-{tissue_source_site}-{participant}-{sample_vial}'


def get_segments(filepath, tcga_id, data_df):
    segment_means = pd.Series(index=data_df.index, name='segment')
    sample_id = parse_tcga_id(tcga_id)

    segments = pd.read_csv(filepath, sep='\t')
    segments['sample_id'] = segments['Sample'].apply(lambda x: parse_tcga_id(x))
    segments = segments.query(f'sample_id == "{sample_id}"')

    for _, row in segments.iterrows():
        query = f"""                                \
            chrom == "chr{row['Chromosome']}" and   \
            start > {row['Start']} and              \
            end < {row['End']}
        """

        index = data_df.query(query).index
        segment_means.iloc[index] = row['Segment_Mean']

    return segment_means


# %%
parser = argparse.ArgumentParser(description="Merges data to single dataframe")
parser.add_argument('--coverage_cancer_file', required=True)
parser.add_argument('--query_file', required=True)
parser.add_argument('--segment_file', required=True)
parser.add_argument('--coverage_blood_file', required=True)
parser.add_argument('--output_file', required=True)
args = parser.parse_args()

# %%
# args = argparse.Namespace()
# args.coverage_cancer_file = \
#     '/faststorage/project/reprator/Andrej/reprator2/data/'\
#     'coverage/BLCA/205bfe9f-2bc9-4236-930c-a862874ad8e0_1000.tsv.gz'

# args.query_file = \
#     '/faststorage/project/reprator/Andrej/reprator2/data/'\
#     'manifests/BLCA.query.tsv'

# args.segment_file = \
#     '/faststorage/project/reprator/Andrej/reprator2/data/'\
#     'segments/BLCA.seg.txt'

# args.coverage_blood_file = \
#     '/faststorage/project/reprator/Andrej/reprator2/data/'\
#     'fixed/blood_means.tsv.gz'

# args.output_file = \
#     '/faststorage/project/reprator/Andrej/reprator2/data/'\
#     'dataframes/BLCA/205bfe9f-2bc9-4236-930c-a862874ad8e0_1000.tsv.gz'

# %%
*_, gdc_id, _, _, _ = re.split('/|_|\\.', args.output_file)

# %%
data_df = pd.read_csv(args.coverage_cancer_file, sep='\t', header=None,
                      names=['chrom', 'start', 'end', 'Ns', 'tumor_coverage'])

tcga_id = convert_gdc2tcga(args.query_file, gdc_id)
data_df['segment'] = get_segments(args.segment_file, tcga_id, data_df)

blood_coverage = pd.read_csv(args.coverage_blood_file, sep='\t', header=None,
                             index_col=0, names=['blood_coverage'])

data_df['blood_coverage'] = blood_coverage.loc[:, 'blood_coverage']

# %%
data_df.to_csv(args.output_file, sep='\t', compression='gzip')
