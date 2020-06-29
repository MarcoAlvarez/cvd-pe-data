#!/bin/bash
cd ./csv/jhu/
python3 ../../code/downloader.py jhu
cd ../../csv/odpe/
python3 ../../code/downloader.py odpe
cd ../../
python3 ./code/generate-json.py
