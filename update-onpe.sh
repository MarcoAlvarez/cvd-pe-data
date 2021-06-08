#!/bin/bash
#
# download files
cd ./onpe-2021-2/
node get_data.js
python3 parse_data.py
cd ../
# commit
date '+%Y/%m/%d %H:%M' | git commit -a -F -
git push origin master
