from dndapi import app
from datetime import datetime

import dndapi.database as database

from flask import render_template

@app.route('/streaminfo/<path:path>')
def render_streaminfo(path=None):
    return render_template('streaminfo.html', content_url="/api/streaminfo/"+path)

@app.route('/api/streaminfo/dmname', methods=['GET',])
def get_dmname():
    dm = database.get_current_dm()
    if dm:
        html = f'<span class="gb">{dm["name"]}</span>'
        return html, 200
    else:
        return '', 404

@app.route('/api/streaminfo/dmkills', methods=['GET',])
def get_dmkills():
    dm = database.get_current_dm()
    if dm:
        html = f'<span class="p2">{dm["numkills"]}</span>'
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
    html = f'<div class="gb" style="font-size: 18px; color:#461B7E">{name}</div><div class="gb" style="font-size: 18px; color:#2C3539;">{clas}</div><div class="p2" style="color:#2C3539;">{time}</div>'
    return html, 200

@app.route('/api/streaminfo/teamkills/<team>', methods=['GET'])
def get_teaminfo(team):
    tks = database.select_dm_teamkills()
    app.logger.info(tks)
    ## Fill in zero kills for losers
    kills = 0
    if team in tks:
        kills = tks[team]
    html = f'<span class="gb">{kills}</span>'
    return html,200

@app.route('/api/streaminfo/peril', methods=['GET'])
def get_peril():
    queued = database.select_queue('queued')
    peril_lvl = min(max(len(queued), 1), 5)
    html = f'<span class="p2" style="color:#461B7E; font-size: 35px;">{peril_lvl}</span>'
    return html, 200

@app.route('/api/streaminfo/graveyard', methods=['GET'])
def get_graveyard():
    dead_chars = database.select_queue('dead')
    html = '<table style="width: 24em;">'
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
    for team in ['sunguard', 'duskpatrol', 'moonwatch']:
        if team in tks:
            totalkills += tks[team]
    html = f'<span class="p2" style="color:#461B7E; font-size: 35px;>{totalkills}</span>'
    return html, 200

@app.route('/api/streaminfo/nextgoal', methods=['GET'])
def get_nextgoal():
    ms = database.get_meta('nextgoal')
    if ms:
        html = f'<span class="p2" style="color:#461B7E; font-size: 35px;>{ms["value"]}</span>'
        return html, 200
    else:
        return '', 404

