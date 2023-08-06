# setup mambaforge
sudo yum install -y zsh tree wget screen git nfs-utils
wget https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh
sh Mambaforge-Linux-x86_64.sh -b -p $HOME/mambaforge
rm -f Mambaforge-Linux-x86_64.sh
./mambaforge/bin/mamba init
exec /bin/bash

# install packages
mkdir -p src/jupyter
cd src/jupyter
gsutil cp gs://ecker-hanqing-src/jupyter/env.yaml ./
mamba env create -f env.yaml
