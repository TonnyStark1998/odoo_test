#!/bin/bash
function remove_slash_if_exists(){
        ARGUMENT=$1
        if [[ "${ARGUMENT:(-1)}" == "/" ]]; then
                return "${ARGUMENT::-1}"
        if
}

function print_usage(){
        echo "./$0 <database_name> <backup_folder> <log_folder>"
}

CURRENT_DATE=`date +%Y%m%d_%H%M`
DATABASE_USER=usr_odoo
DATABASE_NAME=$1
BACKUP_FOLDER_PATH=$2
LOG_FOLDER_PATH=$3

if [[ -z $DATABASE_NAME ]]; then
        echo "Must specify the database name."
        print_usage
        exit -1
fi

if [[ -z $BACKUP_FOLDER_PATH ]]; then
        echo "Must specify the path to save the backup file."
        print_usage
        exit -1
fi

if [[ -z $LOG_FOLDER_PATH ]]; then
        echo "Must specify the path to save the log file."
        print_usage
        exit -1
fi

if [[ ! -d $BACKUP_FOLDER_PATH ]]; then
        echo "$BACKUP_FOLDER_PATH must be a directory."
        exit -2
fi

if [[ ! -e $LOG_FOLDER_PATH ]]; then
        mkdir -p $LOG_FOLDER_PATH
fi

BACKUP_FOLDER_PATH=remove_slash_if_exists $BACKUP_FOLDER_PATH
LOG_FOLDER_PATH=remove_slash_if_exists $LOG_FOLDER_PATH

exec > ${LOG_FOLDER_PATH}/odoo_${DATABASE_NAME}_${CURRENT_DATE}_backup.log 2>&1

DATABASE_FILENAME=odoo_${DATABASE_NAME}_${CURRENT_DATE}.dump
DB_CONTAINER_ID=$(docker container ls -f name=$DATABASE_NAME-odoo-db-1 -q)

docker container exec ${DB_CONTAINER_ID} pg_dump --verbose --no-owner --username ${DATABASE_USER} --format c --no-password -f ${BACKUP_FOLDER_PATH}/${DATABASE_FILENAME} ${DATABASE_NAME}