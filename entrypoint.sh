#!/bin/bash

# Check if the DATABASE_NAME environment variable was set, if not this must fail the start of the container.
if [[ -z ${DATABASE_NAME} ]]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S.%N')][entrypoint.sh] Database name was not specified. Use the environment variable $DATABASE_NAME to specify the name of the database to use for this container."
    exit -1
fi

# Replace all the values about the parameters for connecting to the database specified in the file
#   set in the environment varible ODOO_CONFIG_FILE with the ones specific for this environment.
sed -ie "s/^db_host.*/db_host = $HOST/" $ODOO_CONFIG_FILE
sed -ie "s/^db_port.*/db_port = $PORT/" $ODOO_CONFIG_FILE
sed -ie "s/^db_user.*/db_user = $USER/" $ODOO_CONFIG_FILE
sed -ie "s/^db_password.*/db_password = $PASSWORD/" $ODOO_CONFIG_FILE
sed -ie "s/^db_name.*/db_name = $DATABASE_NAME/" $ODOO_CONFIG_FILE

echo "[$(date '+%Y-%m-%d %H:%M:%S.%N')][entrypoint.sh] Odoo configuration file updated successfully."

# Check if the Odoo edition is CE for this environment, in this case the addons_path configuration must be changed
#   to reflect the correct path for the Community Edition.
if [[ "${ODOO_EDITION,,}" == "ce" ]]; then
    sed -ie "s/^addons_path.*/addons_path = \/mnt\/extra-addons\/common,\/mnt\/extra-addons\/ce/" $ODOO_CONFIG_FILE

    echo "[$(date '+%Y-%m-%d %H:%M:%S.%N')][entrypoint.sh] Addons Paths for Odoo Community Edition updated successfully."
fi

# Test the database settings to check all is good. See the file below to understand what is being checked.
test_database_settings.py

echo "[$(date '+%Y-%m-%d %H:%M:%S.%N')][entrypoint.sh] Database settings testing was successful."

# Initial values to run the Odoo daemon which are common to all editions and versions.
ODOO_ARGS="--config $ODOO_CONFIG_FILE --update all"

# Check whether this is a new database created from scratch or is an old one.
#   If it is a new database we need to install the basic modules to get Odoo up & running.
#   The variable ODOO_DATABASE_STATE is set in the test_database_settings.py Python scripts.
#   See the script file for more details.
if [[ -n $ODOO_DATABASE_STATE 
        && "${ODOO_DATABASE_STATE,,}" == "new" 
        && -n $ODOO_INITIAL_MODULES ]]; then
    ODOO_ARGS=$ODOO_ARGS + " --init ${ODOO_INITIAL_MODULES}"

    echo "[$(date '+%Y-%m-%d %H:%M:%S.%N')][entrypoint.sh] Initial modules set to install on a new database."
fi

# Run the Odoo daemon with the required arguments.
exec odoo $ODOO_ARGS