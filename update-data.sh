#!/bin/bash
#
# download files
cd ./csv/jhu/
python3 ../../code/downloader.py jhu
cd ../../csv/odpe/
python3 ../../code/downloader.py odpe
cd ../../
# parse info
python3 ./code/generate-json.py
# commit
date '+%Y/%m/%d %H:%M' | git commit -a -F -
git push origin master
