from flask import Flask, request
from flask_jwt import JWT
from google.cloud import datastore
import datetime
import logging
import os

app = Flask(__name__)
# read the secretkey.txt file
try:
    secret_key = open('/secretkey.txt','r').readlines()[0].strip()
except:
    secret_key = os.urandom(24).hex()

# Connect to the Google Datastore
datastore_client = datastore.Client()

app.config['SECRET_KEY'] = secret_key
app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(days=1)
app.config['JWT_AUTH_URL_RULE'] = '/api/auth'

#log = logging.getLogger('werkzeug')
#log.setLevel(logging.DEBUG)
#log.addHandler(logging.StreamHandler())

# Deal with CORS
@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  if request.method == 'OPTIONS':
    response.headers['Access-Control-Allow-Methods'] = 'PATCH, GET, POST, PUT'
    headers = request.headers.get('Access-Control-Request-Headers')
    if headers:
      response.headers['Access-Control-Allow-Headers'] = headers
  return response

import dndapi.auth

jwt = JWT(app, dndapi.auth.authenticate, dndapi.auth.identity)

from dndapi.endpoints import index, dms, queue, donors, search, donations, characters
