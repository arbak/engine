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

    # Azure PostgreSQL connection parameters
    host = os.environ.get('HOST')
    dbname = os.environ.get('DATABASE')
    user = os.environ.get('USER_IDENTITY')
    sslmode = 'require'

    # Acquire AAD token
    cred = ManagedIdentityCredential(client_id=os.environ.get('CLIENT_ID'))
    token = cred.get_token('https://ossrdbms-aad.database.windows.net/.default')
    access_token = token.token

    conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname, access_token,
                                                                                 sslmode)
    conn = psycopg2.connect(conn_string)
    logger.info("User name to test: " + user + ".")

    try:
        logger.info("Connection established")
        cursor = conn.cursor()

        # Example parameterized query
        query = "SELECT * FROM public.bag_panden ORDER BY id ASC LIMIT 100"

        # Execute query with parameters
        cursor.execute(query)

        # Fetch results
        rows = cursor.fetchall()
        for row in rows:
            logger.info("User name to test: " + row + ".")

        # Close cursor and connection
        cursor.close()
        conn.close()

    except psycopg2.Error as e:
        print(f"Error: {e}")
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
