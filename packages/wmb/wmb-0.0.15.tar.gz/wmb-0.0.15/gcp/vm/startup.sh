# startup script
# copy analysis files and mount filestore
sudo mount 10.132.160.226:/eckerhome /mnt/home
cd BICCN
# start jupyter
screen -R jupyter
mamba activate wmb

# jupyter-lab --ip=0.0.0.0 --port=8080 --no-browser --NotebookApp.token='USE_YOUR_PW_HERE'
# jupyter-notebook --ip=0.0.0.0 --port=8080 --no-browser --NotebookApp.token='USE_YOUR_PW_HERE'

