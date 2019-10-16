from dndapi import app
from flask import request
from flask_jwt import jwt_required, current_identity
import json
from datetime import datetime

import dndapi.auth as auth
import dndapi.database as database

def press_x_to_json(donation):
    jso = {
        'id': donation['id'],
        'timestamp': donation['timestamp'],
        'amount': str(int(donation['amount'])/100.0),
        'method': donation['method'],
        'donor_id': donation['donor_id']
    }
    return json.dumps(jso)

def validate_donation_post(js):
    # Validate donation object
    if ('amount' in js and
            'method' in js and
            'donor_id' in js):
        try:
            x = float(js['amount'])
            return True
        except:
            return False
    else:
        return False


@app.route('/api/donations/', methods=['GET', 'POST'])
@app.route('/api/donations/<int:donation_id>', methods=['GET'])
@jwt_required()
def get_donations(donation_id=None):
    if request.method == 'GET':
        # get a specific donation. return its json
        if donation_id:
            d = database.get_donation_by_id(donation_id)
            if d:
                return press_x_to_json(d), 200
            else:
                return '', 404
        else:
            # Look for donations with a query string ?donor_id=2
            args = request.args
            if 'donor_id' in args:
                donor_id = args['donor_id']
                donations = database.get_donations_for_donor(donor_id)
                app.logger.info(donations)
                return '[%s]' % ','.join([press_x_to_json(r) for r in donations]), 200, {'Content-Type': 'application/json; charset=utf-8'}
            else:
                return '',404
    elif request.method == 'POST':
        # pull the posted information from json and validate it
        json_data = request.get_json()
        app.logger.info(json_data)
        if not json_data or not validate_donation_post(json_data):
            app.logger.info("shit was bad %s", json_data)
            return '', 400
        else:
            # insert the Donations object
            d = database.insert_donation(int(float(json_data['amount'])*100),
                               json_data['method'],
                               json_data['donor_id'])
            app.logger.info(d)
            if d:
                app.logger.info(d)
                return press_x_to_json(d), 201, {'Content-Type': 'application/json; charset=utf-8'}
            else:
                return '{"error": "Could not insert donation"}', 400, {'Content-Type': 'application/json; charset=utf-8'}
