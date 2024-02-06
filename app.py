import os

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("This message will be logged to application logs")
from azure.identity import ManagedIdentityCredential
app = Flask(__name__)


@app.route('/')
def index():
   print('Request for index page received')
   cred = ManagedIdentityCredential(client_id="6bbe6b4c-aee5-43f6-8845-1646ddb3d95b")
   token = cred.get_token('https://ossrdbms-aad.database.windows.net/.default')
   content = token.token
   logger.info("This message will be logged to application logs: " + str(content[0:2]) + ".")
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
       return render_template('hello.html', name = name)
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))


if __name__ == '__main__':
   app.run()
