#!/bin/bash
CURRENT_DATE=`date +%Y%m%d_%H%M`
DATABASE_NAME=$1
DATABASE_USER=$2

if [[ -n ${DATABASE_NAME} ]]; then
    echo "Must specify the database name."
    exit 1
fi

if [[ -n ${DATABASE_USER} ]]; then
    DATABASE_USER=usr_odoo
fi

DB_CONTAINER_ID=$(docker container ls -f name=$DATABASE_NAME-odoo-db-1 -q)
BACKUP_FILE=$(ls -1t /var/data/production-backups/$DATABASE_NAME | head -1)

exec > /var/log/update_database/${DATABASE_NAME}_${CURRENT_DATE}.log 2>&1

filename_database=odoo_${name_database}_${current_date}.backup

docker container exec $DB_CONTAINER_ID pg_restore --verbose --no-owner --no-privileges --clean --create --if-exists --port 5432 --format t --username $DATABASE_USER --role $DATABASE_USER --password --dbname $DATABASE_NAME /var/data/backups/$BACKUP_FILE

if [[ "$?" -ne 0 ]]; then
    echo "Could not update the database $DATABASE_NAME. Exit code $?"
fi