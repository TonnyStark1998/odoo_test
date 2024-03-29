#!/bin/bash

if [[ -z "$1" ]]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S.%N')][remove_modules_on_odoo_version.sh] You must specify the odoo version as the first argument."
    exit -1
fi

# TODO: Parametrized the BASE_DIR as this can change in the odoo docker official image.
BASE_DIR="/mnt/extra-addons"
echo "[$(date '+%Y-%m-%d %H:%M:%S.%N')][remove_modules_on_odoo_version.sh] Deleting directories from '${BASE_DIR}' except '$1'."

# The extra addons for the different version of Odoo are copied to the $BASE_DIR.
#   Each Odoo version has one directory where the extra addons are added. Ex.: 16.0, 13.0, ...
#   This command finds all the directories which are different from the directory of the Odoo Version 
#   passed by the command line to this script.
#   Example:
#   $1 = 16.0
#   
#   $BASE_DIR                   $BASE_DIR
#   |_ 16.0         after >>    |_16.0
#   |_ 13.0
find $BASE_DIR/* -maxdepth 0 -type d ! -iname $1 -exec rm -rf {} \;