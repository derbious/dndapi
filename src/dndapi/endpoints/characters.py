from dndapi import app
from flask import request
from flask_jwt import jwt_required, current_identity
import json
from datetime import datetime

from sqlalchemy import or_, func

import dndapi.auth as auth
from dndapi.database import Session, Donor, Character, Donation, Dm

def to_json(char):
    jso = {
        'id': char.id,
        'name': char.name,
        'race': char.race,
        'class': char.char_class,
        'state': char.state,
        'num_resses': char.num_resses,
        'queue_pos': char.queue_pos,
        'donor_id': char.donor_id
    }
    if char.starttime:
        jso['starttime'] = char.starttime.isoformat()
    else:
        jso['starttime'] = None
    if char.deathtime:
        jso['deathtime'] = char.deathtime.isoformat()
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
            'donor_id' in js and
            js['donor_id'].isdigit()):
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


@app.route('/characters/', methods=['GET', 'POST'])
@app.route('/characters/<int:character_id>', methods=['GET'])
@jwt_required()
def get_characters(character_id=None):
    if request.method == 'GET':
        # get a specific character. return its json
        if character_id:
            s = Session()
            try:
                character = s.query(Character).filter(Character.id==character_id).one_or_none()
                if character:
                    character_json = to_json(character)
                    return character_json 
                else:
                    return '', 404
            finally:
                s.close()
        else:
            # Look for characters with a query string ?donor_id=2
            args = request.args
            if 'donor_id' in args:
                donor_id = args['donor_id']
                s = Session()
                try:
                    search_results = s.query(Character).filter(Character.donor_id==donor_id).all();
                    if search_results == None:
                        return '[]', 200
                    else:
                        ret = "[%s]"%','.join([to_json(x) for x in search_results])
                        return ret
                finally:
                    s.close()
            else:
                return '',404
    elif request.method == 'POST':
        # pull the posted information from json and validate it
        json_data = request.get_json()
        if not json_data or not validate_new_character_post(json_data):
            return '', 400
        else:
            # insert data into characters table
            new_character = Character(
                name = json_data['name'],
                race = json_data['race'],
                char_class = json_data['char_class'],
                state = 'waiting',
                donor_id = json_data['donor_id'])

            new_donation = Donation(
                donor_id = json_data['donor_id'],
                amount = 5.00,
                reason = 'Character',
                timestamp = datetime.now(),
                method = json_data['fee_type'])

            
            #Grab the maximum queue_pos, and set it
            s = Session()
            try:
                pos_max = s.query(func.max(Character.queue_pos)).filter(Character.state == 'waiting').one_or_none()
                app.logger.info(pos_max)

                if not pos_max[0]:
                    new_pos=1
                else:
                    new_pos = pos_max[0]+1
                new_character.queue_pos = new_pos

                s.add(new_character)
                s.add(new_donation)
                s.commit()
                return "{\"status\": \"ok\"}",201
            finally:
                s.close()



#The /characters/startplay endpoint starts Pulls a character from the
# waiting queue, and starts them playing
@app.route('/characters/startplay/<int:character_id>', methods=['POST',])
@jwt_required()
def rollinitiative(character_id=None):
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
        s = Session()
        try:
            char = s.query(Character).\
                filter(Character.id == character_id).\
                one_or_none()

            if not char:
                return '',400
            # Changes state of character to -playing-
            char.state = 'playing'

            # needed for the math in the UPDATE
            current_queue_pos = char.queue_pos

            # sets the queue_pos to the negative of their seat number
            char.queue_pos = json_data['seat_num'] * -1
            # starts clock
            char.starttime = datetime.now()

            ##subtract 1 from  everything above current_queue_pos
            s.query(Character).\
                filter(Character.state == 'waiting').\
                filter(Character.queue_pos > current_queue_pos).\
                update({Character.queue_pos: Character.queue_pos - 1})

            s.commit()
            return '{"status": "ok"}',201
        except:
            return '',400
        finally:
            s.close()


#The /characters/death endpoint removes the character from play
@app.route('/characters/death/<int:character_id>', methods=['POST',])
@jwt_required()
def characterdeath(character_id=None):
    # Requires Admin token
    if current_identity.username != 'admin':
        return '',401
    if character_id == None:
        return '',400
    else:
        s = Session()
        try:
            char = s.query(Character).\
                filter(Character.id == character_id).\
                first()
            dm = s.query(Dm).\
                filter(Dm.state == 'current').\
                first()
            if not char:
                return '', 400
            char.state = 'dead'
            char.deathtime = datetime.now()
            char.queue_pos = None
            dm.num_kills += 1
            s.commit()
            return "{\"status\": \"ok\"}",201
        except:
            return '',400
        finally:
            s.close()


# the /characters/res/ endpoint ressurects the player (optional cash
# donation associated) admin creds needed
@app.route('/characters/res/<int:character_id>', methods=['POST',])
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
        s = Session()
        try:
            char = s.query(Character).\
                filter(Character.id == character_id).\
                first()
            dm = s.query(Dm).\
                filter(Dm.state == 'current').\
                first()
            if not char:
                return '', 400

            # add res
            char.num_resses = char.num_resses+1
            dm.num_kills += 1
            if json_data['donation'] != None:
                new_donation = Donation(
                    timestamp = datetime.now(),
                    amount = json_data['donation']['amt'],
                    method = json_data['donation']['method'],
                    reason = 'player_res',
                    donor_id = char.donor_id)
                s.add(new_donation)
            s.commit()
            return "{\"status\": \"ok\"}",201
        except:
            return '',400
        finally:
            s.close()

#/characters/graveyard/ endpoint. returns current deaths ranked by
# time alive
@app.route('/characters/graveyard/', methods=['GET'])
@jwt_required()
def graveyard():
    s = Session()
    try:
        deadchars = s.query(Character,Donor).\
            filter(Character.state == 'dead').\
            join(Donor).\
            all()
        if not deadchars:
            return '[]', 200
        jso = []
        for char in deadchars:
            jso.append({
                'name': char.Character.name,
                'player': char.Donor.first_name,
                'seconds_alive': (char.Character.deathtime - char.Character.starttime).total_seconds()
            })
            retjson = json.dumps(sorted(jso, key=lambda k: k['seconds_alive'], reverse=True))
        return retjson,200
    finally:
        s.close()
