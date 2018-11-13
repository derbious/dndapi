from dndapi import app, datastore_client
from flask import request
from flask_jwt import jwt_required, current_identity
import json
from datetime import datetime
from google.cloud import datastore

import dndapi.auth as auth


def to_json(donation):
    jso = {
        'id': donation.id,
        'timestamp': donation['timestamp'].isoformat(),
        'amount': str(donation['amount']),
        'method': donation['method'],
        'reason': donation['reason'],
        'donor_id': donation['donor_id']
    }
    return json.dumps(jso)

def validate_donation_post(js):
    # Validate donation object
    if ('amount' in js and
            'method' in js and
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


@app.route('/api/donations/', methods=['GET', 'POST'])
@app.route('/api/donations/<int:donation_id>', methods=['GET'])
@jwt_required()
def get_donations(donation_id=None):
    if request.method == 'GET':
        # get a specific donor. return its json
        if donation_id:
            key = datastore_client.key('Donation', donation_id)
            entity = datastore_client.get(key)
            if entity:
                return to_json(entity), 200
            else:
                return '', 404
        else:
            # Look for donations with a query string ?donor_id=2
            args = request.args
            if 'donor_id' in args:
                donor_id = args['donor_id']
                query = datastore_client.query(kind='Donation')
                query.add_filter('donor_id', '=', donor_id)
                results = list(query.fetch())
                sorted_results = sorted(results, key=lambda k: k['timestamp'], reverse=True)
                app.logger.info(sorted_results)
                return '[%s]' % ','.join([to_json(r) for r in sorted_results]), 200
            else:
                return '',404
    elif request.method == 'POST':
        # pull the posted information from json and validate it
        json_data = request.get_json()
        if not json_data or not validate_donation_post(json_data):
            app.logger.info("shit was bad %s", json_data)
            return '', 400
        else:
            app.logger.info("it worked well.")
            # insert the Donations object
            key = datastore_client.key('Donation')
            e = datastore.Entity(key=key)
            e['timestamp'] = datetime.now()
            e['amount'] = json_data['amount']
            e['method'] = json_data['method']
            e['reason'] = json_data['reason']
            e['donor_id'] = json_data['donor_id']
            datastore_client.put(e)
            app.logger.info(e)
            return "{\"donation_id\": %s}"%e.id, 201
