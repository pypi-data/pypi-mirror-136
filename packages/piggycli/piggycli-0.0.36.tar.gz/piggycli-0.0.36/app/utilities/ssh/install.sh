#!/bin/bash

# Install CloudHSM-Client
wget https://s3.amazonaws.com/cloudhsmv2-software/CloudHsmClient/EL7/cloudhsm-client-latest.el7.x86_64.rpm

sudo yum install ./cloudhsm-client-latest.el7.x86_64.rpm -y

# Install Python3
sudo yum install python3 -y

# Create Virtual Env
python3 -m venv piggy/env

echo "source ${HOME}/piggy/env/bin/activate" >> ${HOME}/.bashrc

source ~/.bashrc

pip install pip --upgrade

pip install boto3

pip install piggy-scripts