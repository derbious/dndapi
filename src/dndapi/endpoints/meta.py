from dndapi import app
from flask import request
from flask_jwt import jwt_required, current_identity
import json
from jsonschema import validate

import dndapi.auth as auth
import dndapi.database as database

## This is json-schema for validation
META_SCHEMA = {
    "type": "object",
    "required": [
        "key",
        "value"
    ],
    "properties": {
        "key": {"type" : "string"},
        "value": {"type" : "string"}
    }
}

@app.route('/api/meta/<key>', methods=['GET',])
@jwt_required()
def get_meta(key):
    app.logger.info('in /meta/<key>')
    app.logger.info(key)
    md = database.get_meta(key)
    app.logger.info(md)
    if md:
        return json.dumps(md), 200, {'Content-Type': 'application/json; charset=utf-8'}
    else:
        return '', 404

@app.route('/api/meta', methods=['POST',])
@jwt_required()
def post_meta():
    app.logger.info('in /meta [POST]')
    if current_identity.username != 'admin':
        return '', 401
    try:
        json_data = request.get_json()
        validate(json_data, META_SCHEMA)
        database.set_meta(json_data['key'], json_data['value'])
        return "", 201
    except Exception as e:
        app.logger.info('couldnt post new meta')
        app.logger.info(e)
        return '', 400

