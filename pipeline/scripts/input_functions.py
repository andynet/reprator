# %%
import pandas as pd
from string import Template
from glob import glob
import re
# import snakemake


# %%
def get_pairs():
    files = glob('/faststorage/project/reprator/Andrej/reprator2/data/bams/remapped/*/*.bam')
    df = pd.DataFrame(columns=['ctype', 'gdc_id'])
    for i, x in enumerate(files):
        *_, ctype, gdc_id, _ = re.split('/|\\.', x)
        df.loc[i, :] = (ctype, gdc_id)
    df.loc[:, 'data_dir'] = '/faststorage/project/reprator/Andrej/reprator2/data'
    df.loc[:, 'bin_size'] = '1000'
    out_file = '/faststorage/project/reprator/Andrej/reprator2/data/wildcards.tsv'
    df.to_csv(out_file, sep="\t")


# %%
def get_files(wildcards):
    # global variables defined by snakemake are config, rules, checkpoints...
    main_template = rules.main.output[0]
    # main_template = '{data_dir}/dataframes/{ctype}/{file_id}_{bin_size}.lm.log'
    df = pd.read_csv('/faststorage/project/reprator/Andrej/reprator2/data/wildcards.tsv', sep='\t', index_col=0)

    results = []
    for i, row in df.iterrows():
        results.append(main_template.format(**row))

    return results

# cases:
#     wildcard from config {data_dir}
#     literal
#     wildcard which we need to figure out
#     unnecessary extension


# %%
# TODO: unify with get_residuals
def get_residuals_extremes(wildcards):
    manifest = f"{wildcards.data_dir}/manifests/{wildcards.ctype}.filtered.tsv"
    manifest_df = pd.read_csv(manifest, sep='\t')
    file_ids = list(manifest_df['file_id'])
    out = Template(f"{wildcards.data_dir}/residuals/{wildcards.ctype}/$file_id/"
                   f"smoothing_{wildcards.smoothing}/extreme_{wildcards.extreme}/signal.feather")
    return [out.substitute(file_id=file_id) for file_id in file_ids]


# %%
def get_residuals(wildcards):
    manifest = f"{wildcards.data_dir}/manifests/{wildcards.ctype}.filtered.tsv"
    manifest_df = pd.read_csv(manifest, sep='\t')
    file_ids = list(manifest_df['file_id'])
    out = Template(f"{wildcards.data_dir}/residuals/{wildcards.ctype}/$file_id/{wildcards.smoothing}/signal.feather")
    return [out.substitute(file_id=file_id) for file_id in file_ids]


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
def get_remapped_to_signal(wildcards):
    manifest = f"{wildcards.data_dir}/manifests/{wildcards.ctype}.filtered.tsv"
    manifest_df = pd.read_csv(manifest, sep='\t')
    file_ids = list(manifest_df['file_id'])
    out = Template(f"{wildcards.data_dir}/signal/{wildcards.ctype}/$file_id.feather")
    return [out.substitute(file_id=file_id) for file_id in file_ids]


# %%
def get_downloaded_to_remapped(wildcards):
    path = f"{wildcards.data_dir}/bams/original/{wildcards.ctype}/*.bam"
    original = glob(path)
    return [x.replace("original", "remapped") for x in original]


# %%
def get_random_feather(wildcards):
    path = f"{wildcards.data_dir}/signal/*/*.feather"
    paths = glob(path)
    return paths[0]
