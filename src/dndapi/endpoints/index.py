from dndapi import app
from flask_jwt import jwt_required

@app.route("/")
def index():
    return ''

@app.route("/check")
@jwt_required()
def check():
    return ''
