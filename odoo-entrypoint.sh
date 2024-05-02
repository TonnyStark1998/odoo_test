#!/bin/bash

set -e

# Check if the DATABASE_NAME environment variable was set, if not this must fail the start of the container.
if [[ -z ${DATABASE_NAME} ]]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S.%N')][entrypoint.sh] Database name was not specified. Use the environment variable $DATABASE_NAME to specify the name of the database to use for this container."
    exit -1
fi

# Test the database settings to check all is good. See the file below to understand what is being checked.
test_database_settings.py
ODOO_DATABASE_STATE=$(cat /var/lib/odoo/odoo_database_state)

# Initial values to run the Odoo daemon which are common to all editions and versions.
ODOO_ARGS="--config=$ODOO_CONFIG_FILE "

# Set the addons paths based on the ODOO_VERSION and ODOO_EDITION
if [[ -n $USE_DEFAULT_ADDONS_PATH 
        && "${USE_DEFAULT_ADDONS_PATH,,}" == "y" ]]; then
    ODOO_ARGS="$ODOO_ARGS --addons-path=/mnt/extra-addons/${ODOO_VERSION}/common,/mnt/extra-addons/${ODOO_VERSION}/${ODOO_EDITION}"
fi

# Check whether this is a new database created from scratch or is an old one.
#   If it is a new database we need to install the basic modules to get Odoo up & running.
#   The variable ODOO_DATABASE_STATE is set in the test_database_settings.py Python scripts.
#   See the script file for more details.
echo "[$(date '+%Y-%m-%d %H:%M:%S.%N')][entrypoint.sh] Database state: $ODOO_DATABASE_STATE."
echo "[$(date '+%Y-%m-%d %H:%M:%S.%N')][entrypoint.sh] Initial modules: $ODOO_INITIAL_MODULES."
if [[ -n "$ODOO_DATABASE_STATE" 
    && "${ODOO_DATABASE_STATE,,}" == "new" ]]; then
    ODOO_ARGS="$ODOO_ARGS --load-language=es_DO "
    if [[ -n "$ODOO_INITIAL_MODULES" ]]; then
        ODOO_ARGS="$ODOO_ARGS --init ${ODOO_INITIAL_MODULES}"

        echo "[$(date '+%Y-%m-%d %H:%M:%S.%N')][entrypoint.sh] Initial modules set to install/update on a new database."
        echo "[$(date '+%Y-%m-%d %H:%M:%S.%N')][entrypoint.sh] All these ${ODOO_INITIAL_MODULES,,} will be installed."
    fi
fi

if [[ -n "$ODOO_UPDATE_MODULES" ]]; then
    ODOO_ARGS="$ODOO_ARGS --update ${ODOO_UPDATE_MODULES}"

    echo "[$(date '+%Y-%m-%d %H:%M:%S.%N')][entrypoint.sh] All these ${ODOO_UPDATE_MODULES,,} will be updated."
fi

# Run the Odoo daemon with the required arguments.
# TODO: Allow the container to run another command passed by the command line.
exec odoo $ODOO_ARGS