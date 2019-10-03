from dndapi import app
from flask_jwt import jwt_required
from flask import send_from_directory, send_file

staticdir = '/usr/src/dndapi/dndapi/static'

@app.route("/")
def root():
    return send_file(staticdir+"/index.html")

@app.route("/<path:path>")
def index(path):
    return send_from_directory(staticdir, path)   

@app.route("/api/check")
@jwt_required()
def check():
    return 'OK'
