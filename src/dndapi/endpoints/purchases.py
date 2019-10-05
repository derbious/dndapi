from dndapi import app
from flask import request
from flask_jwt import jwt_required, current_identity
import json
from datetime import datetime

import dndapi.auth as auth
import dndapi.database as database

def to_json(purchase):
    jso = {
        'id': donation['id'],
        'timestamp': donation['timestamp'],
        'amount': str(int(donation['amount'])/100.0),
        'reason': donation['reason'],
        'donor_id': donation['donor_id']
    }
    return json.dumps(jso)

def validate_purchase_post(js):
    # Validate donation object
    if ('amount' in js and
        'reason' in js and
        'donor_id' in js and
        js['donor_id'].isdigit()):
        try:
            x = float(js['amount'])
            return True
        except:
            return False
    else:
        return False


@app.route('/api/purchases/', methods=['GET', 'POST'])
@app.route('/api/purchases/<int:donation_id>', methods=['GET'])
@jwt_required()
def get_purchases(purchase_id=None):
    if request.method == 'GET':
        # get a specific purchase. return its json
        if purchase_id:
            d = database.get_purchase_by_id(purchase_id)
            if d:
                return to_json(d), 200, {'Content-Type': 'application/json; charset=utf-8'}
            else:
                return '', 404
        else:
            # Look for purchases with a query string ?donor_id=2
            args = request.args
            if 'donor_id' in args:
                donor_id = args['donor_id']
                purchases = database.get_purchases_for_donor(donor_id)
                app.logger.info(purchases)
                return '[%s]' % ','.join([to_json(r) for r in donations]), 200, {'Content-Type': 'application/json; charset=utf-8'}
            else:
                return '',404
    elif request.method == 'POST':
        # pull the posted information from json and validate it
        json_data = request.get_json()
        app.logger.info(json_data)
        if not json_data or not validate_purchase_post(json_data):
            app.logger.info("shit was not good %s", json_data)
            return '', 400
        else:
            # insert the purchase object
            d = database.insert_donation(int(float(json_data['amount'])*100),
                               json_data['reason'],
                               json_data['donor_id'])
            app.logger.info(d)
            if d:
                app.logger.info(d)
                return to_json(d), 201, {'Content-Type': 'application/json; charset=utf-8'}
            else:
                return '{"error": "Could not insert donation"}', 400, {'Content-Type': 'application/json; charset=utf-8'}
