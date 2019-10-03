from dndapi import app
from flask import request
from flask_jwt import jwt_required, current_identity
import json
from datetime import datetime

import dndapi.auth as auth
import dndapi.database as database

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

def playerqueue_to_json(res):
    jso = {
        'id': res.Character.id,
        'name': res.Character.name,
        'race': res.Character.race,
        'class': res.Character.char_class,
        'state': res.Character.state,
        'num_resses': res.Character.num_resses,
        'queue_pos': res.Character.queue_pos,
        'donor_id': res.Character.donor_id,
        'player_name': res.Donor.first_name,
    }
    if res.Character.starttime:
        jso['starttime'] = res.Character.starttime.isoformat()
    else:
        jso['starttime'] = None
    if res.Character.deathtime:
        jso['deathtime'] = res.Character.deathtime.isoformat()
    else:
        jso['deathtime'] = None
    return json.dumps(jso)

def validate_new_character_post(js):
    # Validate donation object
    if ('name' in js and
            'race' in js and
            'char_class' in js and
            'fee_type' in js and
            'player_id' in js and
            js['player_id'].isdigit()):
        return True
    else:
        return False

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

def validate_res_post(js):
    if 'donation' in js and js['donation'] == None:
        return True
    elif ('donation' in js and
            'amt' in js['donation'] and
            'method' in js['donation']):
        return True
    else:
        return False


@app.route('/api/characters/', methods=['GET', 'POST'])
@app.route('/api/characters/<int:character_id>', methods=['GET'])
@jwt_required()
def get_characters(character_id=None):
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
        # pull the posted information from json and validate it
        json_data = request.get_json()
        if not json_data or not validate_new_character_post(json_data):
            app.logger.info(json_data)
            return '', 400
        else:    
            d = database.insert_character(json_data['name'], json_data['race'], json_data['char_class'], 'queued', json_data['player_id'])
            return "{\"character_id\": %s}"% d['id'], 201, {'Content-Type': 'application/json; charset=utf-8'}

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

        idx = int(json_data['seat_num'])-1
        with datastore_client.transaction():
            characterkey = datastore_client.key('Character', character_id)
            character = datastore_client.get(characterkey)

            waitingqueue_key = datastore_client.key('Playerqueue', 'waiting')
            wq = datastore_client.get(key=waitingqueue_key)

            playingqueue_key = datastore_client.key('Playerqueue', 'playing')
            pq = datastore_client.get(key=playingqueue_key)

            character['state'] = 'playing'
            wq['queue'].remove(character['name'])
            pq['queue'][idx] = character['name']

            character['starttime'] = datetime.now()
            datastore_client.put_multi([character, wq, pq])
        return '{"status": "ok"}', 201

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
        # Get the character
        characterkey = datastore_client.key('Character', character_id)
        character = datastore_client.get(characterkey)
        character['state'] = 'dead'
        character['deathtime'] = datetime.now()

        # Get the DM
        query = datastore_client.query(kind='Dm')
        query.add_filter('current', '=', True)
        dm = list(query.fetch())[0]
        dm['numkills'] += 1
        
        # update the "playing" queue - removing this character
        playingqueue_key = datastore_client.key('Playerqueue', 'playing')
        pq = datastore_client.get(key=playingqueue_key)
        pq['queue'] = ['' if (n == character['name']) else n for n in pq['queue']]
        
        datastore_client.put_multi([character, dm, pq])

        return "{\"status\": \"ok\"}",201

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
        json_data = request.get_json()
        # takes {donation: None} or
        #  {donation: {amt: 40, payment: 'cash'}
        if not json_data or not validate_res_post(json_data):
            return '', 400
        
        # get a specific character. return its json
        ck = datastore_client.key('Character', character_id)
        ce = datastore_client.get(ck)
        ce['num_resses'] += 1
        
        # update the dms kills
        query = datastore_client.query(kind='Dm')
        query.add_filter('current', '=', True)
        dme = list(query.fetch())[0]
        dme['numkills'] += 1
        datastore_client.put_multi([ce, dme])

        if 'donation' in json_data and json_data['donation'] != None:
            dk = datastore_client.key('Donation')
            de = datastore.Entity(key=dk)
            de['donor_id'] = ce['donor_id']
            de['method'] = json_data['donation']['method']
            de['amount'] = json_data['donation']['amt']
            de['reason'] = 'character_res'
            de['timestamp'] = datetime.now()
            datastore_client.put(de)

        return "{\"status\": \"ok\"}",201

#/characters/graveyard/ endpoint. returns current deaths ranked by
# time alive
@app.route('/api/characters/graveyard/', methods=['GET'])
@jwt_required()
def graveyard():
    query = datastore_client.query(kind='Character')
    query.add_filter('state', '=', 'dead')
    jso = []
    for char in list(query.fetch()):
        donorkey = datastore_client.key('Donor', int(char['donor_id']))
        donor = datastore_client.get(donorkey)
        jso.append({
            'name': char['name'],
            'player': donor['firstname'],
            'seconds_alive': (char['deathtime'] - char['starttime']).total_seconds()
        })
    
    retjson = json.dumps(sorted(jso, key=lambda k: k['seconds_alive'], reverse=True))
    return retjson,200
