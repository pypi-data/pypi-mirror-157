#!/bin/bash
# установка Python
# https://www.python.org/ftp/python

PYTHON_VER=$1

sudo apt -y install build-essential zlib1g-dev libncurses5-dev libgdbm-dev
sudo apt -y install libnss3-dev libsqlite3-dev libssl-dev libsqlite3-dev
sudo apt -y install libreadline-dev libffi-dev libbz2-dev liblzma-dev

mkdir ~/temp 
cd ~/temp
wget https://www.python.org/ftp/python/$PYTHON_VER/Python-$PYTHON_VER.tgz
tar -xf Python-$PYTHON_VER.tgz && cd Python-$PYTHON_VER || exit
./configure --enable-optimizations && make -j "$(nproc)"
sudo make altinstall
