#!/bin/bash
current_date=`date +%Y%m%d_%H%M`
name_database=$1

exec > /var/log/odoo/odoo_${name_database}_${current_date}_backup.log 2>&1

if [[ -n ${name_database} ]]; then
        filename_database=odoo_${name_database}_${current_date}.dump

        pg_dump --verbose --no-owner --username postgres --format c --no-password --exclude-table-data *auditlog* -f /var/data/${filename_database} ${name_database}

        if [[ "$?" -eq 0 ]]; then
                mv /var/data/${filename_database} /mnt/odoo-databases-backups-prod/${name_database}/
        fi
else
        echo "Must specify the database name."
fi
