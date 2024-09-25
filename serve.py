#!/usr/bin/env python3

import os, socket, theopenem

from datetime import datetime, timedelta
from flask import Flask, render_template, flash, request, session, redirect, url_for
from flask_session import Session
from redis import Redis

application = Flask(__name__)
application.secret_key = 'asdefxmnHO(N&YO*m7hON*mo8GN&FEHMAjkajdfamo)_'
application.config['SESSION_TYPE'] = 'redis'
application.config['PERMANENT_SESSION_LIFETIME'] = 3600
application.config['SESSION_REDIS'] = Redis.from_url('unix:///run/redis-toem-store/redis.sock')

# set up server-side session
Session(application)
# set up connection to theopenem
toem = theopenem.Theopenem(os.environ.get('TOEMURL'), os.environ.get('TOEMUSER'), os.environ.get('TOEMPASS'))

@application.route('/')
def index():
    # redirect if already logged in
    if 'computer' in session.keys():
        return redirect(url_for('store'))

    # Get hostname by DNS
    reverse_ns = socket.getnameinfo((request.remote_addr, 0), 0)[0].split('.')[0]
    # Search for IP and hostname in Theopenem
    search = toem.computer_search(request.remote_addr) + toem.computer_search(reverse_ns)
    session['computer_potentials'] = search
    # Checkin results
    for r in search:
        toem.computer_checkin(r['Id'])

    # Return loading page
    return render_template('index.html')

@application.route('/login')
def login():
    # send back to index if we skipped a step
    if 'computer_potentials' not in session.keys():
        return redirect(url_for('index'))

    # get new computers after checkins
    potentials = [toem.computer_get(computer['Id']) for computer in session['computer_potentials']]

    # weed out wrong IPs and old checkins
    potentials = [potential for potential in potentials if
                  potential['LastIp'] == request.remote_addr and
                  datetime.fromisoformat(potential['LastCheckinTime']) > datetime.now() - timedelta(minutes=1)]

    # check to see how many individual results we have
    if len(set([i['Id'] for i in potentials])) == 1:
        session['computer'] = potentials[0]
        return(redirect(url_for('store')))

    return render_template('login_failed.html')

@application.route('/store')
def store():
    if 'computer' not in session.keys():
        return(redirect(url_for('index')))

    toem.computer_message(session['computer']['Id'], message='Your computer was successfully identified!', title='Congrats!')

    modules = toem.get_modules('Self-Service')

    return(render_template('store.html', computer=session['computer'], modules=modules))

@application.route('/test')
def test():
    flash('Search: ' + request.remote_addr)
    for result in toem.computer_search(request.remote_addr):
        flash(result)

    reverse_ns = socket.getnameinfo((request.remote_addr, 0), 0)[0].split('.')[0]
    flash('Search: ' + reverse_ns)
    for result in toem.computer_search(reverse_ns):
        flash(result)
    return render_template('store.html', info='# Info!')

@application.route('/run/<guid>')
def run(guid):
    try:
        module_categories = toem.get_module_categories(guid)
    except KeyError as identifier:
        return(redirect(url_for('index')))

    if 'Self-Service' in set([toem.get_category(cat['CategoryId'])['Name'] for cat in module_categories]):
        toem.run_module(session['computer']['Id'], guid)
        return(render_template('run_success.html', module=guid))
    else:
        return(render_template('run_failure.html', module=guid))

if(__name__ == '__main__'):
    application.run(host="0.0.0.0")