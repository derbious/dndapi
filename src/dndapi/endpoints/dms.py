from dndapi import app
from flask import request
from flask_jwt import jwt_required, current_identity
import json
from jsonschema import validate

import dndapi.auth as auth
import dndapi.database as database

## This is json-schema for validation
DM_SCHEMA = {
    "type": "object",
    "required": [
        "name",
        "team"
    ],
    "properties": {
        "name": {"type" : "string"},
        "team": {"type" : "string"}
    }
}

@app.route('/api/currentdm', methods=['GET',])
@jwt_required()
def get_currentdm():
    dm = database.get_current_dm()
    if dm:
        return json.dumps(dm), 200, {'Content-Type': 'application/json; charset=utf-8'}
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
    app.logger.info('entering post_dm()')
    app.logger.info(json_data)
    try:
        validate(json_data, DM_SCHEMA)
        newdm = database.insert_current_dm(json_data['name'], json_data['team'])
        return json.dumps(newdm), 201, {'Content-Type': 'application/json; charset=utf-8'}
    except Exception as e:
        app.logger.info(e)
        return '{\"status\", \"error\"}', 400, {'Content-Type': 'application/json; charset=utf-8'}


@app.route('/api/dmteamkills', methods=['GET',])
@jwt_required()
def team_kills():
    return json.dumps(database.select_dm_teamkills()), 200, {'Content-Type': 'application/json; charset=utf-8'}

