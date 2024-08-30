#!/usr/bin/env python3
import psycopg2
import os
import time
import datetime

if __name__ == '__main__':
    db_host  = os.environ.get('HOST') # Get the database server to use from the environment
    db_port = os.environ.get('PORT') # Get the port to use from the environment when connecting to the database server
    db_user = os.environ.get('USER') # Get the username to use from the environment when connecting to the database server
    db_password = os.environ.get('PASSWORD') # Get the password to use from the environment when connecting to the database server
    db_name = os.environ.get('DB_NAME') # Get the database name to use from the environment when creating this client environment
    default_db_name = 'postgres' # Set the default database to connect to when testing the connection to the server
    max_retries = os.environ.get('MAX_RETRIES') # Get the max number of tries we must do before failing the connection test
    sleep_time = os.environ.get('SLEEP_TIME') # Get the number of seconds to wait between each retry
    odoo_database_state = 'new'

    connection_successful = False
    count_retries = 0

    # If the SLEEP_TIME environment variable was not set, then use 30 as default.
    default_sleep_time = float(sleep_time) if sleep_time else 30
    # If the MAX_RETRIES environment variable was not set, then use 3 as default.
    max_retries = int(max_retries) if max_retries else 3

    while count_retries < max_retries:
        try:
            count_retries += 1
            '''
            Always try to connect to default database just to check
                if the server is Up & Running.
            '''
            print('[{}][test_database_settings.py] #{} try connecting to database: {}'.format(datetime.datetime.now(),
                count_retries,
                default_db_name))
            connection = psycopg2.connect(database=default_db_name,
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password)
            connection_successful = True

            '''
            Check if the database set in the DB_NAME environment variable is created or not.
            '''
            test_db_cursor = connection.cursor()
            test_db_cursor.execute('SELECT datname FROM pg_database WHERE datname = %s', (db_name,))
            if test_db_cursor.rowcount > 0:
                '''
                Set the ODOO_DATABASE_STATE to the value new to indicate that this database does not exist.
                '''
                odoo_database_state = 'old'

            print('[{}][test_database_settings.py] Database name: {}. This is a/an {} database.'.format(datetime.datetime.now(),
                db_name,
                odoo_database_state))

        except Exception as e:
            print('[{}][test_database_settings.py] #{} unsuccessful.'.format(datetime.datetime.now(),
                count_retries,
                db_name))
            for arg in e.args:
                print('[{}][test_database_settings.py] Exception: {}'.format(datetime.datetime.now(), arg))
            connection_successful = False
        else:
            connection.close()

        # If the connection has been successful, then stop the retries.
        if connection_successful:
            print('[{}][test_database_settings.py] Database settings testing was successful.'
                  .format(datetime.datetime.now()))
            break

        # If this is the las retry, don't wait.
        if count_retries != (max_retries - 1):
            print('[{}][test_database_settings.py] Waiting {} seconds to retry.'
                  .format(datetime.datetime.now(), default_sleep_time))
            time.sleep(default_sleep_time)

if not connection_successful:
    print('[{}][test_database_settings.py] Database settings testing failed.'
                  .format(datetime.datetime.now()))
    exit(-1)

file_odoo_database_state = open("/var/lib/odoo/odoo_database_state", "w")
print(odoo_database_state, file=file_odoo_database_state, flush=True)
file_odoo_database_state.close()
