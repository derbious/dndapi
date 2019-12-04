from dndapi import app
from datetime import datetime

import dndapi.database as database

from flask import render_template

@app.route('/streaminfo/<path:path>')
def render_streaminfo(path=None):
    refresh_interval = 5000
    if path in ['graveyard']:
        refresh_interval = 120000
    return render_template('streaminfo.html',
            content_url="/api/streaminfo/"+path,
            refresh_interval=refresh_interval)

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
    name = "&nbsp;"
    clas = "&nbsp;"
    time = "&nbsp;"
    playing = database.select_queue('playing')
    for p in playing:
        if p['q_pos'] == seatnum:
            name = p['name']
            clas = p['class']
            lifetime = (datetime.now() - datetime.fromisoformat(p['start_time'])).seconds
            hours, remainder = divmod(lifetime, 3600)
            minutes, seconds = divmod(remainder, 60)
            time = '{:02}:{:02}'.format(int(hours), int(minutes))
    html = f'<div style="background-color: #9D9A87; padding:20px;"><div class="gb" align="center" style="font-size: 18px; color:#461B7E">{name}</div><div align="center" class="gb" style="font-size: 18px; color:#2C3539;">{clas}</div><div align="center" class="p2" style="color:#2C3539;">{time}</div></div>'
    return html, 200

@app.route('/api/streaminfo/teamkills/<team>', methods=['GET'])
def get_teaminfo(team):
    tks = database.select_dm_teamkills()
    app.logger.info(tks)
    colors = {
        'duskpatrol': '#D08E8C',
        'moonwatch': '#60606F',
        'sunguard': '#C67644'
    }
    ## Fill in zero kills for losers
    kills = 0
    if team in tks:
        kills = tks[team]
    if team in colors:
        color = colors[team]
    else:
        color = '#FFFFFF'
    html = f'<div class="gb" style="color:{color};">{kills}</div>'
    return html,200

@app.route('/api/streaminfo/peril', methods=['GET'])
def get_peril():
    queued = database.select_queue('queued')
    peril_lvl = min(max(len(queued), 1), 5)
    html = f'<div class="p2" style="padding:20px; background-color: #9D9A87; color:#461B7E; font-size: 35px;">{peril_lvl}</div>'
    return html, 200

@app.route('/api/streaminfo/graveyard', methods=['GET'])
def get_graveyard():
    dead_chars = database.select_queue('dead')
    html = '<marquee behavior="scroll" direction="up" scrollamount="2" style="height:600px;"><table style="width: 24em;">'
    for dc in dead_chars:
        lifetime = (datetime.fromisoformat(dc['end_time']) - datetime.fromisoformat(dc['start_time'])).seconds
        hours, remainder = divmod(lifetime, 3600)
        minutes, seconds = divmod(remainder, 60)
        html += '<tr style="vertical-align: bottom;"><td class="gb">{}<td><td class="p2" style="font-size: 20px">{:02}:{:02}</td><tr>'.format(dc['name'], int(hours), int(minutes))
    html += '</table></marquee>'
    return html, 200

@app.route('/api/streaminfo/totalkills', methods=['GET'])
def get_totalkills():
    totalkills = 0
    tks = database.select_dm_teamkills()
    for team in ['sunguard', 'duskpatrol', 'moonwatch']:
        if team in tks:
            totalkills += tks[team]
    html = f'<div class="p2" style="padding:20px; background-color:#9D9A87; color:#461B7E; font-size: 35px;">{totalkills}</div>'
    return html, 200

@app.route('/api/streaminfo/nextgoal', methods=['GET'])
def get_nextgoal():
    ms = database.get_meta('nextgoal')
    if ms:
        html = f'<div class="p2" style="padding:20px; background-color:#9D9A87; color:#461B7E; font-size: 20px;">{ms["value"]}</div>'
        return html, 200
    else:
        return '', 404

