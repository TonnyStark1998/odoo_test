#!/bin/bash

if [[ -z "$1" ]]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S.%N')][remove_modules_on_odoo_version.sh] You must specify the odoo version as the first argument."
    exit -1
fi

BASE_DIR="/mnt/extra-addons"
echo "[$(date '+%Y-%m-%d %H:%M:%S.%N')][remove_modules_on_odoo_version.sh] Deleting directories from '${BASE_DIR}' except '$1'."
find $BASE_DIR/* -maxdepth 0 -type d ! -iname $1 -exec rm -rf {} \;