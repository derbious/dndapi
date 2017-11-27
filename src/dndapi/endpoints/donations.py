from dndapi import app
from flask import request
from flask_jwt import jwt_required, current_identity
import json
from datetime import datetime

from sqlalchemy import or_

import dndapi.auth as auth
from dndapi.database import Session, Donor, Donation


def to_json(donation):
    jso = {
        'id': donation.id,
        'timestamp': donation.timestamp.isoformat(),
        'amount': str(donation.amount),
        'method': donation.method,
        'reason': donation.reason,
        'donor_id': donation.donor_id
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


@app.route('/donations/', methods=['GET', 'POST'])
@app.route('/donations/<int:donation_id>', methods=['GET'])
@jwt_required()
def get_donations(donation_id=None):
    app.logger.info("in get_donations()")
    if request.method == 'GET':
        # get a specific donor. return its json
        if donation_id:
            s = Session()
            try:
                donation = s.query(Donation).filter(Donation.id==donation_id).one_or_none()
                if donation:
                    donation_json = to_json(donation)
                    return donation_json
                else:
                    return '', 404
            finally:
                s.close()
        else:
            # Look for donations with a query string ?donor_id=2
            args = request.args
            if 'donor_id' in args:
                donor_id = args['donor_id']
                s = Session()
                try:
                    search_results = s.query(Donation).filter(Donation.donor_id==donor_id).all();
                    if search_results == None:
                        return '[]', 200
                    else:
                        ret = "[%s]"%','.join([to_json(x) for x in search_results])
                        return ret, 200
                finally:
                    s.close()
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
            # insert data into donors table
            new_donation = Donation(timestamp=datetime.now(),
                    amount=json_data['amount'],
                    method=json_data['method'],
                    reason=json_data['reason'],
                    donor_id=json_data['donor_id'])
            s = Session()
            try:
                s.add(new_donation)
                s.commit()
                return "{\"status\": \"ok\"}",201
            finally:
                s.close()
