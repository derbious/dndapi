from flask import Flask, request
from flask_jwt import JWT
import datetime
import logging
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()
app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(days=1)

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

from dndapi.endpoints import index, search, donors, donations, characters, queue, dms
import dndapi.database

