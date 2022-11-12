#!/bin/bash
CURRENT_DATE=`date +%Y%m%d_%H%M`
DATABASE_NAME=$1
PRODUCTION_SERVER_NAME=vmazlxol8odoofeprod01

if [[ -n ${DATABASE_NAME} ]]; then
    echo "Must specify the database name."
    exit 1
fi

if [[ $DATABASE_NAME -eq "accounterprise" ]]; then
    rsync -vr -e "ssh -p 6546" samuel.luciano@$PRODUCTION_SERVER_NAME:/var/data/odoo/filestore /var/data/$DATABASE_NAME/odoo/
else
    rsync -vr -e "ssh -p 6546" samuel.luciano@$PRODUCTION_SERVER_NAME:/var/data/odoo-$DATABASE_NAME/filestore /var/data/$DATABASE_NAME/odoo/
fi

if [[ "$?" -ne 0 ]]; then
    echo "Could not update the filestore for database $DATABASE_NAME. Exit code $?"
fi