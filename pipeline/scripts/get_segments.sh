#!/usr/bin/env bash

# default argument
data_dir=/faststorage/project/reprator/Andrej/reprator2/data

# argument parsing
while [ $# -gt 0 ]; do
    case "$1" in
        -d|--data_dir)
            data_dir="$2"
            shift 2
            ;;
        *)
            break
            ;;
    esac
done

# set up the environment
segment_dir=${data_dir}/segments
mkdir -p ${segment_dir}
cd ${segment_dir}


# downloaded html to see what data is available
wget "http://gdac.broadinstitute.org/runs/stddata__2016_01_28/data" \
    -O names.html

# parse available directories
less names.html \
    | grep -P '\[DIR\]' \
    | cut -f 5 -d " " \
    | cut -f 2 -d "\"" \
    | tr -d "/" > names.txt

# remove html
rm names.html


for name in $(cat names.txt); do

    # download data
    wget "http://gdac.broadinstitute.org/runs/stddata__2016_01_28/data/${name}\
/20160128/gdac.broadinstitute.org_${name}.Merge_snp__genome_wide_snp_6__broad_\
mit_edu__Level_3__segmented_scna_hg19__seg.Level_3.2016012800.0.0.tar.gz"   \
        -O "${name}".tar.gz;

    # unpack data
    tar -xvzf "${name}".tar.gz;

    # rename data
    mv "gdac.broadinstitute.org_${name}.Merge_snp__genome_wide_snp_6__broad_mi\
t_edu__Level_3__segmented_scna_hg19__seg.Level_3.2016012800.0.0/${name}.snp__g\
enome_wide_snp_6__broad_mit_edu__Level_3__segmented_scna_hg19__seg.seg.txt" \
        "${name}".seg.txt;

    # remove redundant data
    rm "${name}".tar.gz;
    rm -r gdac*;

    # extract unique IDs
    less ${name}.seg.txt \
        | cut -f1 \
        | tail -n +2 \
        | sort \
        | uniq > "${name}".uniq.txt; 
done;

# remove failed attempts for uniq file
find . -size 0 -exec rm -i {} \;

