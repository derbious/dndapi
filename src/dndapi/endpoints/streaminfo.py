from dndapi import app
from datetime import datetime

import dndapi.database as database

@app.route('/streaminfo/dm', methods=['GET',])
def get_dm():
    app.logger.info('in currentdm/')
    dm = database.get_current_dm()
    if dm:
        html = f'{dm["name"]}: {dm["numkills"]} kills'
        return html, 200
    else:
        return '', 404

@app.route('/streaminfo/player/<int:seatnum>', methods=['GET'])
def get_player(seatnum):
    name = ""
    clas = ""
    playing = database.select_queue('playing')
    for p in playing:
        if p['q_pos'] == seatnum:
            name = p['name']
            clas = p['class']
    html = f'P{seatnum}: {name} {clas} ##TIMER##'
    return html, 200

@app.route('/streaminfo/teaminfo', methods=['GET'])
def get_teaminfo():
    tks = database.select_dm_teamkills()
    ## Fill in zero kills for losers
    for team in ['dawnguard', 'duskpatrol', 'nightwatch']:
        if team not in tks:
            tks[team] = 0
    html = f'Duskpatrol: {tks["duskpatrol"]}<br>Nightwatch: {tks["nightwatch"]}<br>Dawnguard: {tks["dawnguard"]}'
    return html, 200

@app.route('/streaminfo/peril', methods=['GET'])
def get_peril():
    queued = database.select_queue('queued')
    peril_lvl = min(max(len(queued), 1), 5)
    html = f'Peril Level: {peril_lvl}'
    return html, 200

@app.route('/streaminfo/graveyard', methods=['GET'])
def get_graveyard():
    dead_chars = database.select_queue('dead')
    html = ""
    for dc in dead_chars:
        lifetime = (datetime.fromisoformat(dc['end_time']) - datetime.fromisoformat(dc['start_time'])).seconds
        hours, remainder = divmod(lifetime, 3600)
        minutes, seconds = divmod(remainder, 60)
        html += '{}     {:02}:{:02}<br>'.format(dc['name'], int(hours), int(minutes))
    return html, 200