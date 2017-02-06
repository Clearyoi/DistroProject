import os
import Cipher as C
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, json


app = Flask(__name__)
knownServerKey = 12

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'fileServer.db'),
    DEBUG=True,
    SECRET_KEY='ServerKEY',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('files.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


def getLevel(token):
    info = json.loads(C.decrypt(token, knownServerKey))
    return info["level"]


def getKey(token):
    info = json.loads(C.decrypt(token, knownServerKey))
    return info["key"]


def getName(token):
    info = json.loads(C.decrypt(token, knownServerKey))
    return info["username"]


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/add', methods=['POST'])
def add_entry():
    return "add pls"


@app.route('/get', methods=['POST'])
def get_entry():
    return "get pls"
