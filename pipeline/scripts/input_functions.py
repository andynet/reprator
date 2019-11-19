import pandas as pd
from string import Template
from glob import glob


# %%
def get_file_ids(wildcards):
    manifest = f"{wildcards.data_dir}/manifests/{wildcards.ctype}.filtered.tsv"
    manifest_df = pd.read_csv(manifest, sep='\t')
    file_ids = list(manifest_df['file_id'])
    out = Template(f"{wildcards.data_dir}/bams/remapped/{wildcards.ctype}/$file_id.bam")
    return [out.substitute(file_id=file_id) for file_id in file_ids]


# %%
def get_download_ids(wildcards):
    manifest = f"{wildcards.data_dir}/manifests/{wildcards.ctype}.filtered.tsv"
    manifest_df = pd.read_csv(manifest, sep='\t')
    file_ids = list(manifest_df['file_id'])
    out = Template(f"{wildcards.data_dir}/bams/original/{wildcards.ctype}/$file_id.bam")
    return [out.substitute(file_id=file_id) for file_id in file_ids]


# %%
def get_downloaded_to_remapped(wildcards):
    path = f"{wildcards.data_dir}/bams/original/{wildcards.ctype}/*.bam"
    original = glob(path)
    return [x.replace("original", "remapped") for x in original]
