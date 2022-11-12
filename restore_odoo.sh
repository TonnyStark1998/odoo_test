!#/bin/sh
docker compose --env-file .docker-compose-env up --force-recreate --detach

DATABASE_USER=usr_odoo
DATABASE_NAME=accounterprise
ODOO_CONTAINER_ID=$(docker container ls -f name=accounterprise-odoo-ee-1 -q)
DB_CONTAINER_ID=$(docker container ls -f name=accounterprise-odoo-db-1 -q)
BACKUP_FILE=$(ls -1t /var/data/production-backups/$DATABASE_NAME | head -1)
PRODUCTION_SERVER_NAME=vmazlxol8odoofeprod01

# TODO: Test to check whether the container ids are empty or not

# Stop Odoo container until database is restored
docker container stop $ODOO_CONTAINER_ID

# Stop and start the Postgres container to close all user connections
docker container stop $DB_CONTAINER_ID
docker container start $DB_CONTAINER_ID

# Drop the database
docker container exec $DB_CONTAINER_ID psql -U usr_odoo -d postgres -c "DROP DATABASE $DATABASE_NAME;"

# Create the empty database
docker container exec $DB_CONTAINER_ID psql -U usr_odoo -d postgres -c "CREATE DATABASE $DATABASE_NAME WITH TEMPLATE template0 OWNER $DATABASE_USER;"

# Restore last database backup
docker container exec $DB_CONTAINER_ID pg_restore --verbose --no-owner --no-privileges --clean --create --if-exists --port 5432 --format t --username $DATABASE_USER --role $DATABASE_USER --password --dbname $DATABASE_NAME /var/data/backups/$BACKUP_FILE

# Copy Odoo files from production server
scp -prvP 6546 samuel.luciano@$PRODUCTION_SERVER_NAME:/var/data/odoo/* /var/data/$DATABASE_NAME/odoo

# Start Odoo container now that the database has been restored
docker container start $ODOO_CONTAINER_ID