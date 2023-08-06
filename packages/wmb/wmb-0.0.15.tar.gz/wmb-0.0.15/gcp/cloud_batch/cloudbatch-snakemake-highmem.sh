#!/bin/bash
# highmem - 32vCPU with 256GB ram
# use case: cloudbatch-snakemake-highmem.sh <gcs bucket name> <project ID> <seq name> <reference folder>
# eg: cloudbatch-snakemake-highmem.sh ecker-snm3c-novaseq 220602-HumanNovaSeqTest M1C_3C_001_Plate1-1-F3 mm10

# fix the python3 environment issue with gsutil
rm /usr/bin/python3
ln -s /opt/conda/envs/mapping/bin/python3 /usr/bin/python3

#prepare the folder structure in the docker container
#Since we do not have the NFS share, we added the 2nd PD /mnt/data to the VM.
ln -s /mnt/data /
mkdir -p /data/NovaSeq
mkdir -p /mnt/data/ref/$4

#coping all reference data and process data from cloud location
gsutil -m cp -n -r gs://ecker-genome-reference/$4/* /mnt/data/ref/$4/.
gsutil cp gs://$1/$2/mapping_config.ini /data/NovaSeq/.
gsutil -m cp -n -r gs://$1/$2/$3 /data/NovaSeq/.

#Processing the Snakemake 
source activate mapping
snakemake -d /data/NovaSeq/$3 --snakefile /data/NovaSeq/$3/Snakefile -j 16 --resources mem_mb=240000

#Moving the result to the GCS location
gsutil -m cp -n -r /data/NovaSeq/$3/* gs://$1/$2/$3/

