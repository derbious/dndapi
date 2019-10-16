from dndapi import app
import flask
from flask_jwt import jwt_required, current_identity
import json

import dndapi.auth as auth
import dndapi.database as database

@app.route('/api/search', methods=['GET',])
@jwt_required()
def search():
    args = flask.request.args
    if 'q' in args:
        q = args['q']
        result_array = []
        donors = database.get_all_donors()
        app.logger.info(donors)
        for r in donors:
            if q in r['first_name'] or q in r['last_name'] or q in r['email_address']:
                result_array.append(r)
        if result_array == None:
            return '[]', 200
        else:
            ret = "[%s]"%','.join([json.dumps(x) for x in result_array])
            return ret
    else:
        return '', 200
