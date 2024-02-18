import os
import logging
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

    connection = psycopg2.connect(conn_string + ' password=' + accessToken.token)
    print("Connection established")
    logger.info("Connection established")
    connection.close()

    return render_template('index.html')


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
