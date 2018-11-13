from dndapi import app, datastore_client
import flask
from flask_jwt import jwt_required, current_identity
import json

import dndapi.auth as auth
from dndapi.endpoints.donors import to_json


@app.route('/api/search', methods=['GET',])
@jwt_required()
def search():
    args = flask.request.args
    if 'q' in args:
        q = args['q']
        result_array = []
        query = datastore_client.query(kind='Donor')
        for r in list(query.fetch()):
            if q in r['firstname'] or q in r['lastname'] or q in r['email']:
                result_array.append(r)
        
        if result_array == None:
            return '[]', 200
        else:
            ret = "[%s]"%','.join([to_json(x) for x in result_array])
            return ret
    else:
        return '', 200
