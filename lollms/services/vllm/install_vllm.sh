#!/bin/bash

# Check if miniconda3/bin/conda exists
if [ -e "$HOME/miniconda3/bin/conda" ]; then
    echo "Conda is installed!"
else
    echo "Conda is not installed. Please install it first."
    echo Installing conda
    curl -LO https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    ./Miniconda3-latest-Linux-x86_64.sh -b
    rm ./Miniconda3-latest-Linux-x86_64.sh
    echo Done
fi
echo "Initializing conda"
$HOME/miniconda3/bin/conda init --all
export PATH
echo "Installing vllm"
$HOME/miniconda3/bin/conda create -n vllm python=3.9 -y
echo "Activating vllm environment"
$HOME/miniconda3/bin/conda activate vllm 
pip install vllm
echo "Done"
