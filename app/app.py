"""
    zaab1t-index
    ~~~~~~~~~~~~

    A video categoriser.

    :copyright: (c) 2017 by Carl Bordum Hansen.
    :licence: MIT, see LICENSE for more details.
"""

import os
import sqlite3
from functools import wraps
from flask import (Flask, render_template, session, request, redirect,
    url_for, g,)


app = Flask(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'zaab1t.db'),
    DEBUG=True,
    SECRET_KEY='shh top secret',
    USERNAME='admin',
    PASSWORD='default',
))
app.config.from_envvar('ZAAB1T-INDEX_SETTINGS', silent=True)


@app.cli.command('createdb')
def createdb_command():
    """Create the database with the schema specified in schema.sql."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    print('Successfully created database!')


def get_db():
    """Return (and create, if necessary) the database connection for the
    current application context."""
    if not hasattr(g, 'sqlite3_db'):
        rv = sqlite3.connect(app.config['DATABASE'])
        rv.row_factory = sqlite3.Row
        g.sqlite3_db = rv
    return g.sqlite3_db


@app.teardown_appcontext
def close_db(error):
    """Close the database connection (if there is one) at the end of a
    request."""
    if hasattr(g, 'sqlite3_db'):
        g.sqlite3_db.close()


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
