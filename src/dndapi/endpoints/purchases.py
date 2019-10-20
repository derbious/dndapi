from dndapi import app
from flask import request
from flask_jwt import jwt_required, current_identity
import json
from jsonschema import validate
from datetime import datetime

import dndapi.auth as auth
import dndapi.database as database

## This is json-schema for validation
PURCHASE_SCHEMA = {
    "type": "object",
    "required": [
        "donor_id",
        "reason",
        "amount"
    ],
    "properties": {
        "reason": {"type" : "string"},
        "amount": {"type" : "number"},
        "donor_id": {"type": "integer"}
    }
}

@app.route('/api/purchases/', methods=['GET', 'POST'])
@app.route('/api/purchases/<int:donation_id>', methods=['GET'])
@jwt_required()
def get_purchases(purchase_id=None):
    if request.method == 'GET':
        # get a specific purchase. return its json
        if purchase_id:
            d = database.get_purchase_by_id(purchase_id)
            if d:
                return json.dumps(d), 200, {'Content-Type': 'application/json; charset=utf-8'}
            else:
                return '', 404
        else:
            # Look for purchases with a query string ?donor_id=2
            args = request.args
            if 'donor_id' in args:
                donor_id = args['donor_id']
                purchases = database.get_purchases_for_donor(donor_id)
                #app.logger.info(purchases)
                return '[%s]' % ','.join([json.dumps(r) for r in purchases]), 200, {'Content-Type': 'application/json; charset=utf-8'}
            else:
                return '',404
    elif request.method == 'POST':
        # pull the posted information from json and validate it
        json_data = request.get_json()
        app.logger.info('purchases[POST]: json_data')
        app.logger.info(json_data)
        try:
            validate(json_data, PURCHASE_SCHEMA)
            # insert the purchase object
            d = database.insert_purchase(int(float(json_data['amount'])*100),
                               json_data['reason'],
                               json_data['donor_id'])
            app.logger.info('purchases[POST]: got past validate')
            if d:
                return json.dumps(d), 201, {'Content-Type': 'application/json; charset=utf-8'}
            else:
                return '{"error": "Could not insert donation"}', 400, {'Content-Type': 'application/json; charset=utf-8'}
        except Exception as e:
            app.logger.info('Purchase json failed validation')
            app.logger.info(e)
            return '', 400
