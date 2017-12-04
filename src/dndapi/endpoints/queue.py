from dndapi import app
from flask import request
from flask_jwt import jwt_required, current_identity
import json
from datetime import datetime

from sqlalchemy import or_, func

import dndapi.auth as auth
from dndapi.database import Session, Donor, Character, Donation

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


#The /queue endpoint returns the ordered player queue
@app.route('/queue/', methods=['GET',])
@jwt_required()
def queue():
    s = Session()
    try:
        playing_res = s.query(Character, Donor).\
            join(Donor).\
            filter(Character.state == 'playing').\
            all()
        waiting_res = s.query(Character, Donor).\
            join(Donor).\
            filter(Character.state == 'waiting').\
            order_by(Character.queue_pos).\
            all()

        playingjson_list = []
        for i in range(6):
            found = False
            for c in playing_res:
                if c.Character.queue_pos == -1 * (i+1):
                    playingjson_list.append(playerqueue_to_json(c))
                    found = True
            if not found:
                playingjson_list.append('null')

        playingjson = '['+','.join(playingjson_list)+']'
        waitingjson = '['+','.join([playerqueue_to_json(c) for c in waiting_res])+']'
        retjson = '{"playing": '+playingjson+', "waiting": '+waitingjson+'}'
        return retjson,200
    finally:
        s.close()


# The /queue/reorder endpoint
@app.route('/queue/reorder/', methods=['POST'])
@jwt_required()
def reorderqueue():
    json_data = request.get_json()
    # Takes {id:#, to_pos:#} and moves alters the queue
    if not json_data or not validate_reorderqueue_post(json_data):
        return '', 400
    else:
        s = Session()
        try:
            char = s.query(Character).\
              filter(Character.id == json_data['id']).\
              one_or_none()
            if char.queue_pos > json_data['to_pos']:
                # moving forward in queue
                s.query(Character).\
                    filter(Character.state == 'waiting').\
                    filter(Character.queue_pos >= json_data['to_pos']).\
                    filter(Character.queue_pos < char.queue_pos).\
                    update({Character.queue_pos: Character.queue_pos + 1})
                char.queue_pos = json_data['to_pos']
            else:
                # moving backward in queue
                # check to see if our to_pos is greater than the queue.
                # if it is, fix it
                pos_max = s.query(func.max(Character.queue_pos)).\
                    filter(Character.state == 'waiting').\
                    one_or_none()[0]
                if json_data['to_pos'] > pos_max:
                    json_data['to_pos'] = pos_max
                s.query(Character).\
                    filter(Character.state == 'waiting').\
                    filter(Character.queue_pos <= json_data['to_pos']).\
                    filter(Character.queue_pos > char.queue_pos).\
                    update({Character.queue_pos: Character.queue_pos - 1})
                char.queue_pos = json_data['to_pos']
            s.commit()
            return '{"status": "ok"}',201
        except:
            return '',400
        finally:
            s.close()


# The /queue/remove/ endpoint removes a player from the queue
@app.route('/queue/remove/<int:character_id>', methods=['POST'])
@jwt_required()
def queue_remove(character_id=None):
    if not character_id:
        return '',400
    s = Session()
    try:
        char = s.query(Character).\
            filter(Character.id == character_id).\
            one_or_none()
        previous_queue_pos = char.queue_pos
        char.state = 'canceled'
        char.queue_pos = None
        if previous_queue_pos:
            # reshuffle everyone forward
            s.query(Character).\
                filter(Character.state == 'waiting').\
                filter(Character.queue_pos >= previous_queue_pos).\
                update({Character.queue_pos: Character.queue_pos - 1})
        s.commit()
        return '{"status": "ok"}',201
    except:
        return '',400
    finally:
        s.close()

# The /queue/unremove/ endpoint places the character back in the queue
@app.route('/queue/unremove/<int:character_id>', methods=['POST'])
@jwt_required()
def queue_unremove(character_id=None):
    if not character_id:
        return '',400
    s = Session()
    try:
        char = s.query(Character).\
            filter(Character.id == character_id).\
            one_or_none()
        pos_max = s.query(func.max(Character.queue_pos)).\
                filter(Character.state == 'waiting').\
                one_or_none()
        if not pos_max[0]:
            new_pos=1
        else:
            new_pos = pos_max[0]+1
        char.state = 'waiting'
        char.queue_pos = new_pos
        s.commit()
        return '{"status": "ok"}',201
    except:
        return '',400
    finally:
        s.close()

