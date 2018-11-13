from dndapi import app, datastore_client
from flask import request
from flask_jwt import jwt_required, current_identity
import json
from google.cloud import datastore

import dndapi.auth as auth

def to_json(donor):
    jso = {
        'id': donor.id,
        'firstname': donor['firstname'],
        'lastname': donor['lastname'],
        'email': donor['email'],
        'address': donor['address']
    }
    if 'dci' in donor:
        jso['dci'] = donor['dci']
    return json.dumps(jso)

def validate_donor_post(js):
    if ('id' not in js and 
            'firstname' in js and
            'lastname' in js and
            'email' in js and
            'address' in js):
        return True
    else:
        return False


@app.route('/api/donors/', methods=['POST',])
@app.route('/api/donors/<int:donor_id>', methods=['GET'])
@jwt_required()
def get_donors(donor_id=None):
    if request.method == 'GET':
        # get a specific donor. return its json
        if donor_id:
            key = datastore_client.key('Donor', donor_id)
            entity = datastore_client.get(key)
            app.logger.info(key)
            app.logger.info(entity)
            if entity:
                return to_json(entity), 200
            else:
                return '', 404
        else:
            return '',404
    elif request.method == 'POST':
        # pull the posted information from json and validate it
        app.logger.info("method was post")
        json_data = request.get_json()
        app.logger.debug("json_data = %s", json_data)
        if not json_data or not validate_donor_post(json_data):
            return '', 400
        else:
            # Check to see if the donor isn't already there
            query = datastore_client.query(kind='Donor')
            query.add_filter('email', '=', json_data['email'])
            if len(list(query.fetch())) > 0:
                return '{\"error\": \"Already exists\"}', 400

            # insert the Donor object
            key = datastore_client.key('Donor')
            app.logger.info(key)
            entity = datastore.Entity(key=key)
            entity['firstname'] = json_data['firstname']
            entity['lastname'] = json_data['lastname']
            entity['email'] = json_data['email']
            entity['address'] = json_data['address']
            entity['dci'] = json_data.get('dci', '')
            datastore_client.put(entity)
            app.logger.info(entity)
            return "{\"donor_id\": %s}"%entity.id, 201
