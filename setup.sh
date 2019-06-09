#! /bin/bash

sudo apt-get update
sudo apt-get install -y python3.7
sudo apt-get install -y python3-pip python3-dev
sudo apt-get install -y python3-venv
sudo apt-get install -y python3.7-venv
python3 -m venv myvenv
source setup2.sh
