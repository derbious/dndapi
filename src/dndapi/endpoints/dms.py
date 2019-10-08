from dndapi import app
from flask import request
from flask_jwt import jwt_required, current_identity
import json

import dndapi.auth as auth
import dndapi.database as database

def to_json(dm):
    jso = {
        'id': dm['id'],
        'name': dm['name'],
        'team': dm['team'],
        'numkills': dm['numkills'],
        'current': dm['current']
    }
    return json.dumps(jso)

def validate_dms_post(js):
    # Need {name: "", team=""}
    if ('name' in js and 
          'team' in js):
        return True
    else:
        return False

@app.route('/api/currentdm', methods=['GET',])
@jwt_required()
def get_currentdm():
    dm = database.get_current_dm()
    if dm:
        return to_json(dm), 200, {'Content-Type': 'application/json; charset=utf-8'}
    else:
        return '', 404

@app.route('/api/dms', methods=['POST',])
@jwt_required()
def post_dm():
    # require admin creds
    if current_identity.username != 'admin':
        return '', 401
    # pull the posted information from json and validate it
    json_data = request.get_json()
    if not json_data or not validate_dms_post(json_data):
        return '', 400
    else:
        database.insert_current_dm(json_data['name'], json_data['team'])
        return '{\"status\", \"ok\"}', 201, {'Content-Type': 'application/json; charset=utf-8'}


@app.route('/api/dmteamkills', methods=['GET',])
@jwt_required()
def team_kills():
    return json.dumps(database.select_dm_teamkills()), 200, {'Content-Type': 'application/json; charset=utf-8'}

