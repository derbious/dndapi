from dndapi import app
from flask import request
from flask_jwt import jwt_required, current_identity
import json
from datetime import datetime
from jsonschema import validate

import dndapi.auth as auth
import dndapi.database as database

## This is json-schema for validation of new_char posts
NEWCHAR_SCHEMA = {
    "type": "object",
    "required": [
        "name",
        "race",
        "char_class",
        "player_id",
        "benefactor_id"
    ],
    "properties": {
        "name": {"type" : "string"},
        "race": {"type" : "string"},
        "char_class": {"type" : "string"},
        "player_id": {"type": "integer"},
        "benefactor_id": {"type": "integer"}
    }
}

RES_SCHEMA = {
    "type": "object",
    "required": [
        "character_id",
        "benefactor_id"
    ],
    "properties": {
        "character_id": {"type" : "integer"},
        "benefactor_id": {"type" : "integer"}
    }
}

def to_json(char):
    jso = {
        'id': char['id'],
        'name': char['name'],
        'race': char['race'],
        'class': char['class'],
        'state': char['state'],
        'num_resses': char['num_resses'],
        'player_id': char['player_id']
    }
    if 'starttime' in char:
        jso['starttime'] = char['starttime'].isoformat()
    else:
        jso['starttime'] = None
    if 'deathtime' in char:
        jso['deathtime'] = char['deathtime'].isoformat()
    else:
        jso['deathtime'] = None
    return json.dumps(jso)

def validate_reorderqueue_post(js):
    # Validate reorderqueue data
    if ('id' in js and
        'to_pos' in js and
        js['to_pos'] > 0):
        return True
    else:
        return False

def validate_startplay_post(js):
    if 'seat_num' in js:
        return True
    else:
        return False

@app.route('/api/characters/', methods=['GET', 'POST'])
@app.route('/api/characters/<int:character_id>', methods=['GET'])
@jwt_required()
def characters(character_id=None):
    if request.method == 'GET':
        if character_id:
            # get a specific character. return its json
            character = database.get_character_by_id(character_id)
            if character:
                return to_json(character), 200, {'Content-Type': 'application/json; charset=utf-8'}
            else:
                return '', 404
        else:
            # Look for characters with a query string ?player_id=2
            args = request.args
            if 'player_id' in args:
                chars = database.get_characters_for_player(args['player_id'])
                j = '[%s]'%','.join([to_json(c) for c in chars])
                return j, 200, {'Content-Type': 'application/json; charset=utf-8'}
            else:
                return '', 404
    elif request.method == 'POST':
        json_data = request.get_json()
        try:
            validate(json_data, NEWCHAR_SCHEMA)
            d = database.insert_character(
                json_data['name'],
                json_data['race'],
                json_data['char_class'],
                'queued',
                json_data['player_id'],
                json_data['benefactor_id'])
            return "{\"character_id\": %s}"% d['id'], 201, {'Content-Type': 'application/json; charset=utf-8'}

            # insert the character
        except Exception as e:
            app.logger.info('newchar json failed validation')
            app.logger.info(e)
            return '', 400

@app.route('/api/characters/forplayer/<int:player_id>', methods=['GET',])
@jwt_required()
def characters_for_player(player_id=None):
    if request.method == 'GET':
        if player_id:
            # get a specific character. return its json
            characters = database.get_characters_for_player(player_id)
            return "["+ ','.join([to_json(c) for c in characters])+"]", {'Content-Type': 'application/json; charset=utf-8'}
        else:
            return '[]', 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route('/api/characters/startplay/<int:character_id>', methods=['POST',])
@jwt_required()
def rollinitiative(character_id=None):
    ### The /characters/startplay endpoint starts Pulls a character from the
    ### waiting queue, and starts them playing
    # Requires Admin token
    if current_identity.username != 'admin':
        return '',401
    if character_id == None:
        return '',400
    else:
        json_data = request.get_json()
        # Takes {seat_num: #} and starts their play
        if not json_data or not validate_startplay_post(json_data):
            return '', 400
        app.logger.info(json_data)

        app.logger.info('Starting character')
        seat = int(json_data['seat_num'])
        database.character_start(character_id, seat)
        return '{"status": "ok"}', 201, {'Content-Type': 'application/json; charset=utf-8'}

#The /characters/death endpoint removes the character from play
@app.route('/api/characters/death/<int:character_id>', methods=['POST',])
@jwt_required()
def characterdeath(character_id=None):
    # Requires Admin token
    if current_identity.username != 'admin':
        return '',401
    if character_id == None:
        return '',400
    else:
        database.character_death(character_id)
        return '{"status": "ok"}', 201, {'Content-Type': 'application/json; charset=utf-8'}

# the /characters/res/ endpoint ressurects the player (optional cash
# donation associated) admin creds needed
@app.route('/api/characters/res/<int:character_id>', methods=['POST',])
@jwt_required()
def characterres(character_id=None):
    # Requires Admin token
    if current_identity.username != 'admin':
        return '',401
    if character_id == None:
        return '',400
    else:
        try:
            json_data = request.get_json()
            validate(json_data, RES_SCHEMA)
            database.character_res(json_data['character_id'], json_data['benefactor_id'])
            return "{\"status\": \"ok\"}",201
        except Exception as e:
            app.logger.info('ressurect post failed validation')
            app.logger.info(e)
            return '', 400

