#!/bin/sh

sudo apt-get update -y && apt-get install -y gcc gfortran libopenmpi-dev openmpi-bin openmpi-common openmpi-doc binutils

pip3 install -r requirements.txt --no-cache-dir
python3 manage.py migrate
python3 manage.py runserver 8000