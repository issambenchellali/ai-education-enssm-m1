#!/bin/bash
apt-get update
apt-get install -y libpq-dev python3-dev
pip install --upgrade pip
pip install -r requirements.txt
