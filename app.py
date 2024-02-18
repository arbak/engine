import os
from flask import Response
import logging
import subprocess
import psycopg2
from dotenv import load_dotenv
from azure.identity import ManagedIdentityCredential
from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)

# Load environment variables from the .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("This message will be logged to application logs")

app = Flask(__name__)


@app.route('/')
def index():
    print('Request for index page received')

    # For user-assigned identity.
    managed_identity_client_id = os.environ.get('AZURE_POSTGRESQL_CLIENTID')
    cred = ManagedIdentityCredential(client_id=managed_identity_client_id)

    logger.info("This Client new Identificatie ID: {}".format(cred))

    # Acquire the access token
    accessToken = cred.get_token('https://ossrdbms-aad.database.windows.net/.default')
    logger.info("Access Token: {}".format(accessToken))

    # Combine the token with the connection string from the environment variables added by Service Connector to
    # establish the connection.
    conn_string = os.environ.get('AZURE_POSTGRESQL_CONNECTIONSTRING')
    logger.info("Connection established")
    logger.info("This conn string: {}".format(conn_string))

    # Define the hostname to ping
    hostname_to_ping = "dev-bbn1-01-dbhost.postgres.database.azure.com"

    # Execute the ping command
    ping_process = subprocess.run(["ping", "-c", "1", hostname_to_ping], capture_output=True, text=True)

    # Check the return code to determine if the ping was successful
    if ping_process.returncode == 0:
        logger.info("Host {} is reachable".format(hostname_to_ping))
    else:
        logger.error("Host {} is not reachable".format(hostname_to_ping))

    # Print out the connection string before attempting to connect
    logger.info("Attempting to establish connection with connection string: {}".format(conn_string))

    # Print out the full connection string including the password token
    full_conn_string = conn_string + ' password=' + accessToken.token
    logger.info("Full connection string: {}".format(full_conn_string))

    try:
        connection = psycopg2.connect(full_conn_string)
        logger.info("Postgresql connection established successfully")
    except psycopg2.Error as e:
        logger.error("Error connecting to PostgreSQL: {}".format(e))

    try:

        cursor = connection.cursor()
        logger.info("This conn string: {}".format(cursor))

        # Example parameterized query
        query = "SELECT identificatie FROM public.bag_panden ORDER BY id ASC LIMIT 7"

        # Execute query with parameters
        cursor.execute(query)

        # Fetch results
        rows = cursor.fetchall()
        for row in rows:
            print(row)
            logger.info("This conn string: {}".format(row))

        # Close cursor and connection
        cursor.close()
        connection.close()

        # Returning rows list as plain text response
        rows_text = '\n'.join([str(row) for row in rows])
        return Response(rows_text, mimetype='text/plain')


    except psycopg2.Error as e:
        print(f"Error: {e}")
        # In case of error, return an error response
        return Response("Error occurred while fetching data.", status=500, mimetype='text/plain')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/hello', methods=['POST'])
def hello():
    name = request.form.get('name')

    if name:
        print('Request for hello page received with name=%s' % name)
        return render_template('hello.html', name=name)
    else:
        print('Request for hello page received with no name or blank name -- redirecting')
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
