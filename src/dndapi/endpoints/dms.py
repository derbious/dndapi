from dndapi import app, datastore_client
from flask import request
from flask_jwt import jwt_required, current_identity
import json
from google.cloud import datastore

import dndapi.auth as auth

def to_json(dm):
    jso = {
        'id': dm.id,
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

@app.route('/api/currentdm/', methods=['GET',])
@jwt_required()
def get_currentdm():
    query = datastore_client.query(kind='Dm')
    query.add_filter('current', '=', True)
    return to_json(list(query.fetch())[0]), 200


@app.route('/api/dms/', methods=['POST',])
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
        # Clear out the old current DM
        query = datastore_client.query(kind='Dm')
        query.add_filter('current', '=', True)
        for dm in list(query.fetch()):
            dm['current'] = False
            datastore_client.put(dm)

        # Create the new Dm entity
        dm_key = datastore_client.key('Dm')
        de = datastore.Entity(key=dm_key)
        de['name'] = json_data['name']
        de['numkills'] = 0
        de['current'] = True
        de['team'] = json_data['team']
        datastore_client.put(de)
        
    return '{\"status\", \"ok\"}', 201


@app.route('/api/dmteamkills/', methods=['GET',])
@jwt_required()
def team_kills():
    retobj = {
        'duskpatrol': 0,
        'moonwatch': 0,
        'sunguard': 0
    }
    # Search duskpatrol
    query = datastore_client.query(kind='Dm')
    query.add_filter('team', '=', "Duskpatrol")
    for dm in list(query.fetch()):
        retobj['duskpatrol'] += dm['numkills']

    query = datastore_client.query(kind='Dm')
    query.add_filter('team', '=', "Moonwatch")
    for dm in list(query.fetch()):
        retobj['moonwatch'] += dm['numkills']
        query = datastore_client.query(kind='Dm')

    query.add_filter('team', '=', "Sunguard")
    for dm in list(query.fetch()):
        retobj['sunguard'] += dm['numkills']

    return json.dumps(retobj), 200

