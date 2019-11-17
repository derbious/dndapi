from dndapi import app
from flask import request
from flask_jwt import jwt_required, current_identity
import json
from datetime import datetime
import dndapi.database as database

def validate_reorderqueue_post(js):
    # Validate reorderqueue data
    if ('id' in js and
        'to_pos' in js and
        js['to_pos'] > 0):
        return True
    else:
        return False

#The /queue endpoint returns the ordered player queue
@app.route('/api/queue/', methods=['GET',])
@jwt_required()
def queue():
    # Store the playing queue in a list of 6
    playing = [None, None, None, None, None, None]
    for p in database.select_queue('playing'):
        app.logger.info(p)
        playing[p['q_pos']-1] = p
    waiting = database.select_queue('queued')
    app.logger.info(waiting)
    res = {
        'playing': playing,
        'waiting': waiting
    }
    return json.dumps(res), 200, {'Content-Type': 'application/json; charset=utf-8'}


# The /queue/remove/ endpoint removes a player from the queue
@app.route('/api/queue/remove/<int:character_id>', methods=['POST'])
@jwt_required()
def queue_remove(character_id=None):
    if not character_id:
        return '',400
    database.queue_remove(character_id)
    return '{"status": "ok"}', 201

# The /queue/unremove/ endpoint removes a player from the queue
@app.route('/api/queue/unremove/<int:character_id>', methods=['POST'])
@jwt_required()
def queue_unremove(character_id=None):
    if not character_id:
        return '',400
    database.queue_unremove(character_id)
    return '{"status": "ok"}', 201

# # The /api/queue/unremove/ endpoint places the character back in the queue
# @app.route('/api/queue/unremove/<int:character_id>', methods=['POST'])
# @jwt_required()
# def queue_unremove(character_id=None):
#     if not character_id:
#         return '',400
#     with datastore_client.transaction():
#         characterkey = datastore_client.key('Character', character_id)
#         character = datastore_client.get(characterkey)

#         waitingqueue_key = datastore_client.key('Playerqueue', 'waiting')
#         wq = datastore_client.get(key=waitingqueue_key)

#         if character['name'] not in wq['queue'] and character['state'] == 'canceled':
#             wq['queue'].append(character['name'])
#             character['state'] = 'waiting'
#             datastore_client.put_multi([character, wq])
#     return '{"status": "ok"}', 201


# The /queue/reorder endpoint
# @app.route('/api/queue/reorder/', methods=['POST'])
# @jwt_required()
# def reorderqueue():
#     json_data = request.get_json()
#     # Takes {id:#, to_pos:#} and moves alters the queue
#     if not json_data or not validate_reorderqueue_post(json_data):
#         return '', 400
#     else:
#         # Get the character name
#         characterkey = datastore_client.key('Character', int(json_data['id']))
#         character = datastore_client.get(characterkey)
        
#         # get the queue
#         waitingqueue_key = datastore_client.key('Playerqueue', 'waiting')
#         wq = datastore_client.get(key=waitingqueue_key)
#         app.logger.info(wq)
#         newqueue = []
#         index = 1
#         placed = False
#         for item in wq['queue']:
#             if index == int(json_data['to_pos']):
#                 # This is where the character is to be placed
#                 newqueue.append(character['name'])
#                 newqueue.append(item)
#                 index += 1
#                 placed = True
#             elif item != character['name']:
#                 # non-character item
#                 newqueue.append(item)
#                 index += 1
#         if not placed:
#             # place in the end, if it is the last position
#             newqueue.append(character['name'])
#         wq['queue'] = newqueue
#         datastore_client.put(wq)
#         return '{"status": "ok"}',201


# # The /queue/remove/ endpoint removes a player from the queue
# @app.route('/api/queue/remove/<int:character_id>', methods=['POST'])
# @jwt_required()
# def queue_remove(character_id=None):
#     if not character_id:
#         return '',400
#     # Get the character for the id
#     with datastore_client.transaction():
#         characterkey = datastore_client.key('Character', character_id)
#         character = datastore_client.get(characterkey)

#         waitingqueue_key = datastore_client.key('Playerqueue', 'waiting')
#         wq = datastore_client.get(key=waitingqueue_key)

#         if character['name'] in wq['queue']:
#             character['state'] = 'canceled'
#             wq['queue'].remove(character['name'])
#             datastore_client.put_multi([character, wq])
#     return '{"status": "ok"}', 201

# # The /api/queue/unremove/ endpoint places the character back in the queue
# @app.route('/api/queue/unremove/<int:character_id>', methods=['POST'])
# @jwt_required()
# def queue_unremove(character_id=None):
#     if not character_id:
#         return '',400
#     with datastore_client.transaction():
#         characterkey = datastore_client.key('Character', character_id)
#         character = datastore_client.get(characterkey)

#         waitingqueue_key = datastore_client.key('Playerqueue', 'waiting')
#         wq = datastore_client.get(key=waitingqueue_key)

#         if character['name'] not in wq['queue'] and character['state'] == 'canceled':
#             wq['queue'].append(character['name'])
#             character['state'] = 'waiting'
#             datastore_client.put_multi([character, wq])
#     return '{"status": "ok"}', 201

