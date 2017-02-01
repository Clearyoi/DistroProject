import os
import random
import Cipher as C
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify

directoryServerUrl = 'http://localhost:3000/'
knownServerKey = 12


# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'authServer.db'),
    SECRET_KEY='ServerKEY',
    DEBUG=True,
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
    with app.open_resource('users.sql', mode='r') as f:
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


def generateLoginResponse():
    newKey = random.randint(1, 26)
    responce = {'key': newKey}
    token = {}
    token['key'] = C.encrypt(str(newKey), knownServerKey)
    token['level'] = C.encrypt(str(2), knownServerKey)
    responce['token'] = token
    return responce


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_users():
    db = get_db()
    cur = db.execute('select username from users order by username asc')
    entryNames = []
    while True:
        row = cur.fetchone()
        if row is None:
            break
        entryNames.append(row["username"])
    return str(entryNames)


@app.route('/login', methods=['POST'])
def login():
    db = get_db()
    error = 'Invalid username or password'
    cur = db.execute('select * from users where username = ?', [request.form['username']])
    row = cur.fetchone()
    if row is None:
        return error
    elif request.form['password'] != row["password"]:
        return error
    else:
        return jsonify(generateLoginResponse())


@app.route('/addUser', methods=['POST'])
def addUser():
    db = get_db()
    cur = db.execute('select username from users where username = ?', [request.form['username']])
    row = cur.fetchone()
    if row is None:
        print request.form['level'] + request.form['username'] + request.form['password']
        db.execute('insert into users (username, password, level) values (?, ?, ?)',
                   [request.form['username'], request.form['password'], request.form['level']])
        db.commit()
        return 'user added'
    else:
        return 'username already exists'


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_files'))
