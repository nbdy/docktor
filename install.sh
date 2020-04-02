#!/usr/bin/bash

cd /tmp/
git clone https://github.com/smthnspcl/docktor
cd docktor
sudo python3 setup.py install
cd /tmp/
sudo rm -rf docktor