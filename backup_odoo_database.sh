#!/bin/bash
CURRENT_DATE=`date +%Y%m%d_%H%M`
DATABASE_NAME=$1
BACKUP_FOLDER_PATH=$2

if [[ -z $DATABASE_NAME ]]; then
        echo "Must specify the database name."
        exit -1
fi

if [[ -z $BACKUP_FOLDER_PATH ]]; then
        echo "Must specify the path to save the backup file."
        exit -1
fi

if [[ ! -d $BACKUP_FOLDER_PATH ]]; then
        echo "$BACKUP_FOLDER_PATH must be a directory."
        exit -2
fi

exec > /var/log/odoo/odoo_${DATABASE_NAME}_${CURRENT_DATE}_backup.log 2>&1

DATABASE_FILENAME=odoo_${DATABASE_NAME}_${CURRENT_DATE}.dump

pg_dump --verbose --no-owner --username postgres --format c --no-password -f ${BACKUP_FOLDER_PATH}${DATABASE_FILENAME} ${DATABASE_NAME}