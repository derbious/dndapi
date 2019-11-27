from dndapi import app
from datetime import datetime

import dndapi.database as database

from flask import render_template

@app.route('/streaminfo/<path:path>')
def render_streaminfo(path=None):
    return render_template('streaminfo.html', content_url="/api/streaminfo/"+path)

@app.route('/api/streaminfo/dm', methods=['GET',])
def get_dm():
    dm = database.get_current_dm()
    if dm:
        html = f'<div class="gb">{dm["name"]}</div><span class="p2">{dm["numkills"]} KILLS</span>'
        return html, 200
    else:
        return '', 404

@app.route('/api/streaminfo/ticker', methods=['GET',])
def get_ticker():
    tick = database.get_meta('ticker')
    if tick:
        html = f'<div class="gb">{tick["value"]}</div>'
        return html, 200
    else:
        return '', 404

@app.route('/api/streaminfo/player/<int:seatnum>', methods=['GET'])
def get_player(seatnum):
    name = ""
    clas = ""
    time = ""
    playing = database.select_queue('playing')
    for p in playing:
        if p['q_pos'] == seatnum:
            name = p['name']
            clas = p['class']
            lifetime = (datetime.now() - datetime.fromisoformat(p['start_time'])).seconds
            hours, remainder = divmod(lifetime, 3600)
            minutes, seconds = divmod(remainder, 60)
            time = '{:02}:{:02}'.format(int(hours), int(minutes))
    html = f'<div class="gb">{name}</div><div class="gb">{clas}</div><div class="p2">{time}</div>'
    return html, 200

@app.route('/api/streaminfo/teaminfo', methods=['GET'])
def get_teaminfo():
    tks = database.select_dm_teamkills()
    ## Fill in zero kills for losers
    for team in ['dawnguard', 'duskpatrol', 'nightwatch']:
        if team not in tks:
            tks[team] = 0
    html = f'<div class="gb">Duskpatrol: {tks["duskpatrol"]}</div><div class="gb">Nightwatch: {tks["nightwatch"]}</div><div class="gb">Dawnguard: {tks["dawnguard"]}</div>'
    return html, 200

@app.route('/api/streaminfo/peril', methods=['GET'])
def get_peril():
    queued = database.select_queue('queued')
    peril_lvl = min(max(len(queued), 1), 5)
    html = f'<div class="p2">PERIL LEVEL:</div><div class="p2">{peril_lvl}</div>'
    return html, 200

@app.route('/api/streaminfo/graveyard', methods=['GET'])
def get_graveyard():
    dead_chars = database.select_queue('dead')
    html = '<table style="width: 20em;">'
    for dc in dead_chars:
        lifetime = (datetime.fromisoformat(dc['end_time']) - datetime.fromisoformat(dc['start_time'])).seconds
        hours, remainder = divmod(lifetime, 3600)
        minutes, seconds = divmod(remainder, 60)
        html += '<tr style="vertical-align: bottom;"><td class="gb">{}<td><td class="p2" style="font-size: 20px">{:02}:{:02}</td><tr>'.format(dc['name'], int(hours), int(minutes))
    html += '</table>'
    return html, 200

@app.route('/api/streaminfo/totalkills', methods=['GET'])
def get_totalkills():
    totalkills = 0
    tks = database.select_dm_teamkills()
    for team in ['dawnguard', 'duskpatrol', 'nightwatch']:
        if team in tks:
            totalkills += tks[team]
    html = f'<div class="p2">TOTAL KILLS:</div><div class="p2">{totalkills}</div>'
    return html, 200

@app.route('/api/streaminfo/nextgoal', methods=['GET'])
def get_nextgoal():
    ms = database.get_meta('nextgoal')
    if ms:
        html = f'<div class="p2">NEXT MILESTONE:</div><div class="p2">{ms["value"]}</div>'
        return html, 200
    else:
        return '', 404

