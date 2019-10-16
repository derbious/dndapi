from dndapi import app
from flask import request
from flask_jwt import jwt_required, current_identity
import json

import dndapi.auth as auth
import dndapi.database as database

def validate_donor_post(js):
    if ('id' not in js and 
            'first_name' in js and
            'last_name' in js and
            'email_address' in js and
            'physical_address' in js):
        return True
    else:
        return False

@app.route('/api/donors', methods=['POST',])
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
                return json.dumps(d), 200, {'Content-Type': 'application/json; charset=utf-8'}
            else:
                return '{"error": "donor not found"}', 404, {'Content-Type': 'application/json; charset=utf-8'}
        else:
            return '{"error": "no donor_id provided"}', 404, {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == 'POST':
        # pull the posted information from json and validate it
        #app.logger.info("method was post")
        json_data = request.get_json()
        app.logger.info(json_data)
        ##app.logger.debug("json_data = %s", json_data)
        if not json_data or not validate_donor_post(json_data):
            app.logger.info('/api/donors POST failed validation')
            return '', 400
        else:
            # make dci availabe if not entered
            if 'dci_number' not in json_data:
                json_data['dci_number'] = None
            # insert the new donor
            app.logger.info(json_data)
            ins_donor = database.insert_new_donor(json_data['first_name'],
                                      json_data['last_name'],
                                      json_data['physical_address'],
                                      json_data['dci_number'],
                                      json_data['email_address'] )
            return json.dumps(ins_donor), 201, {'Content-Type': 'application/json; charset=utf-8'}
