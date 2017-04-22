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
    url_for, g, abort,)


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
def createdb():
    """Create the database with the schema specified in schema.sql."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    print('Successfully created database!')


@app.cli.command('updatedb')
def updatedb():
    """Add all videos from /videos to the database, if they are not in it."""
    folder = os.getcwd() + '/videos/'
    db = get_db()
    videos = db.cursor().execute('select * from video').fetchall()
    video_titles = set(video['filename'] for video in videos)
    for file in os.listdir(folder):
        if file in video_titles:
            continue
        statement = 'insert into "video" ("filename") values ("%s");' % file
        db.cursor().execute(statement)
        db.commit()
        video_titles.add(file)


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


def get_video_by_id(ID):
    db = get_db()
    db_query = 'select * from "video" where "id" = ?', ID
    return db.cursor().execute(*db_query).fetchone()


@app.route('/')
@login_required
def index():
    """Provide the user with a listing of all videos."""
    db = get_db()
    db_query = 'select * from "video"'
    videos = db.cursor().execute(db_query).fetchall()
    return '\n'.join([str(video['id']) for video in videos])


@app.route('/video/<ID>')
@login_required
def show_video(ID):
    """Return a page with one video."""
    video = get_video_by_id(ID)
    if not video:
        abort(404)
    return 'video found'


@app.route('/video/<ID>/edit', methods=['GET', 'POST'])
@login_required
def edit_video(ID):
    """Return a page with the video and a form to edit its' attributes."""
    video = get_video_by_id(ID)
    if not video:
        abort(404)
    return str(video['id'])


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


@app.errorhandler(404)
def page_not_found(e):
    return '404 Not Found', 404
