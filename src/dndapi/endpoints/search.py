from dndapi import app
import flask
from flask_jwt import jwt_required, current_identity
import json

from sqlalchemy import or_

import dndapi.auth as auth
from dndapi.database import Session, Donor
from dndapi.endpoints.donors import to_json


@app.route('/search', methods=['GET',])
@jwt_required()
def search():
    args = flask.request.args
    if 'q' in args:
        q = args['q']
        result_array = []
        s = Session()
        try:
            like_str = '%{}%'.format(q)
            result_array = result_array + s.query(Donor).filter(or_(Donor.first_name.like(like_str), Donor.last_name.like(like_str), Donor.email_address.like(like_str))).all()
            if result_array == None:
                return '[]', 200
            else:
                ret = "[%s]"%','.join([to_json(x) for x in result_array])
                return ret
        finally:
            s.close()
    else:
        return '', 200
