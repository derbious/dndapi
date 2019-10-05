from flask import Flask, request, redirect
from flask_jwt import JWT
import datetime
import logging
import os
import sqlite3

app = Flask(__name__)
# read the secretkey.txt file
try:
    secret_key = open('/secretkey.txt','r').readlines()[0].strip()
except:
    secret_key = os.urandom(24).hex()

# Connect to the Google Datastore
##datastore_client = datastore.Client()

app.config['SECRET_KEY'] = secret_key
app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(days=1)
app.config['JWT_AUTH_URL_RULE'] = '/api/auth'

# Redirect to HTTPS iff we have a "HTTPS" env variable
perform_https_redirect = os.getenv('HTTPS', "false") == "true"

# Create all of the database stuff
import dndapi.database
dndapi.database.makedb()

app.logger.info("perform_https_redirect: %s", perform_https_redirect)

@app.before_request
def https_redirect():
    if perform_https_redirect and request.headers.get('X-Forwarded-Proto', None) == 'http':
        return redirect(request.url.replace('http://', 'https://'), 301)

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

from dndapi.endpoints import index, donors, search, donations, characters, purchases
###queue, dms
