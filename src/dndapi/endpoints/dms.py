from dndapi import app
from flask import request
from flask_jwt import jwt_required, current_identity
import json

from sqlalchemy import or_, func

import dndapi.auth as auth
from dndapi.database import Session, Dm


def to_json(dm):
    jso = {
        'id': dm.id,
        'name': dm.name,
        'team': dm.team,
        'numkills': dm.num_kills,
        'state': dm.state
    }
    return json.dumps(jso)

def validate_dms_post(js):
    # Need {name: "", team=""}
    if ('name' in js and 
          'team' in js):
        return True
    else:
        return False


@app.route('/currentdm/', methods=['GET',])
@jwt_required()
def get_currentdm():
    s = Session()
    try:
        currentdm = s.query(Dm).\
            filter(Dm.state == 'current').\
            one_or_none()
        if currentdm:
            res = to_json(currentdm)
            return to_json(currentdm), 200
        else:
            return '', 404
    finally:
        s.close()


@app.route('/dms/', methods=['POST',])
@jwt_required()
def post_dm():
    # require admin creds
    if current_identity.username != 'admin':
        return '', 401
    # pull the posted information from json and validate it
    json_data = request.get_json()
    if not json_data or not validate_dms_post(json_data):
        return '', 400
    else:
        # insert data into Dms table
        new_dm = Dm(name=json_data['name'],
                team=json_data['team'],
                num_kills = 0,
                state = 'current')
        s = Session()
        # change previous current dm to not being it
        try:
            s.query(Dm).\
                filter(Dm.state == 'current').\
                update({Dm.state: None})
            s.add(new_dm)
            s.commit()
            s.flush()
            return '{"result": "ok"}', 201
        except:
            return '', 400
        finally:
            s.close()

@app.route('/dmteamkills/', methods=['GET',])
@jwt_required()
def team_kills():
    s = Session()
    try:
        teams = s.query(Dm.team, func.sum(Dm.num_kills)).group_by(Dm.team).all()
        retobj = {
            'duskpatrol': 0,
            'moonwatch': 0,
            'dawnguard': 0
        }
        for r in teams:
            if r[0].lower() in retobj:
                retobj[r[0].lower()] += int(r[1])
        return json.dumps(retobj), 200
    except:
        return '', 400
    finally:
        s.close()

