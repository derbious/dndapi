from dndapi import app
from flask import request
from flask_jwt import jwt_required, current_identity
import json

import dndapi.auth as auth
import dndapi.database as database

def to_json(d):
    jso = {
        'id': d['id'],
        'first_name': d['first_name'],
        'last_name': d['last_name'],
        'email_address': d['email_address'],
        'physical_address': d['physical_address']
    }
    if 'dci_number' in d:
        jso['dci_number'] = d['dci_number']
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
            app.logger.info(donor_id)
            d = database.get_donor_by_id(donor_id)
            app.logger.info(d)
            if d:
                return to_json(d), 200, {'Content-Type': 'application/json; charset=utf-8'}
            else:
                return '{"error": "donor not found"}', 404, {'Content-Type': 'application/json; charset=utf-8'}
        else:
            return '{"error": "no donor_id provided"}', 404, {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == 'POST':
        # pull the posted information from json and validate it
        #app.logger.info("method was post")
        json_data = request.get_json()
        ##app.logger.debug("json_data = %s", json_data)
        if not json_data or not validate_donor_post(json_data):
            return '', 400
        else:
            # make dci availabe if not entered
            if 'dci' not in json_data:
                json_data['dci'] = None
            # insert the new donor
            app.logger.info(json_data)
            ins_donor = database.insert_new_donor(json_data['firstname'],
                                      json_data['lastname'],
                                      json_data['address'],
                                      json_data['dci'],
                                      json_data['email'] )
            return to_json(ins_donor), 201, {'Content-Type': 'application/json; charset=utf-8'}
