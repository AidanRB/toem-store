#!/usr/bin/env python3

import os, socket, toem, redis

from flask import Flask, render_template, flash, request
from flask_session import Session

app = Flask(__name__)
app.secret_key = 'asdefxmnHO(N&YO*m7hON*mo8GN&FEHMAjkajdfamo)_'
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True

t = toem.Toem(os.environ.get('TOEMURL'), os.environ.get('TOEMUSER'), os.environ.get('TOEMPASS'))

@app.route('/')
def main():
    # Get hostname by DNS
    reverse_ns = socket.getnameinfo((request.remote_addr, 0), 0)[0].split('.')[0]
    # Search for IP and hostname in Theopenem
    search = t.search(request.remote_addr) + t.search(reverse_ns)
    # Checkin results
    for r in search:
        t.checkin(r['Id'])

    # Return loading page
    return render_template('init.html')

@app.route('/test')
def test():
    flash('Search: ' + request.remote_addr)
    for result in t.search(request.remote_addr):
        flash(result)

    reverse_ns = socket.getnameinfo((request.remote_addr, 0), 0)[0].split('.')[0]
    flash('Search: ' + reverse_ns)
    for result in t.search(reverse_ns):
        flash(result)
    return render_template('store.html', info='# Info!')

if(__name__ == '__main__'):
    app.run(host="0.0.0.0")