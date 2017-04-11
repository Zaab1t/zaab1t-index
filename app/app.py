"""
    zaab1t-index
    ~~~~~~~~~~~~

    A video categoriser.

    :copyright: (c) 2017 by Carl Bordum Hansen.
    :licence: MIT, see LICENSE for more details.
"""

import os
from functools import wraps
from flask import Flask, render_template, session, request, redirect, url_for


app = Flask(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'zaab1t.db'),
    DEBUG=True,
    SECRET_KEY='shh top secret',
    USERNAME='admin',
    PASSWORD='default',
))
app.config.from_envvar('ZAAB1T-INDEX_SETTINGS', silent=True)


def login_required(f):
    """Redirect the user to /login, if not logged in. Used as an innermost
    decorator."""
    @wraps(f)
    def inner(*args, **kwargs):
        if session.get('logged_in'):
            return f(*args, **kwargs)
        return redirect(url_for('login', next=request.url))
    return inner


@app.route('/')
@login_required
def index():
    return 'SEARCH FOR VIDEOS'


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Provide the user with a form to login."""
    error = None
    if request.method == 'POST':
        correct_name = request.form['username'] == app.config['USERNAME']
        correct_pass = request.form['password'] == app.config['PASSWORD']
        if correct_name and correct_pass:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            error = 'Invalid credentials.'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    """Log the user out and redirect him/her to /login."""
    session.pop('logged_in', None)
    return redirect(url_for('login'))
