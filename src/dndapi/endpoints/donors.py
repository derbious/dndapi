from dndapi import app
from flask import request
from flask_jwt import jwt_required, current_identity
import json

from sqlalchemy import or_

import dndapi.auth as auth
from dndapi.database import Session, Donor


def to_json(donor):
    jso = {
        'id': donor.id,
        'firstname': donor.first_name,
        'lastname': donor.last_name,
        'email': donor.email_address,
        'address': donor.physical_address
    }
    if donor.dci_number:
        jso['dci'] = donor.dci_number
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


@app.route('/donors/', methods=['POST',])
@app.route('/donors/<int:donor_id>', methods=['GET'])
@jwt_required()
def get_donors(donor_id=None):
    app.logger.info("in get_donors()")
    if request.method == 'GET':
        # get a specific donor. return its json
        if donor_id:
            s = Session()
            donor = s.query(Donor).filter(Donor.id==donor_id).one_or_none()
            if donor:
                donor_json = to_json(donor)
                s.close()
                return donor_json
            else:
                s.close()
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
            # insert data into donors table
            new_donor = Donor(first_name=json_data['firstname'],
                    last_name=json_data['lastname'],
                    email_address=json_data['email'],
                    physical_address=json_data['address'],
                    dci_number=json_data.get('dci', None))
            s = Session()
            s.add(new_donor)
            try:
                s.commit()
                s.flush()
                returntext = "{\"donor_id\": %s}"%new_donor.id
                returnval = 201
            except:
                returnval = 400
                returntext = ''
            finally:
                s.close()
            return returntext,returnval
