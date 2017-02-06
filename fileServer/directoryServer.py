import os
import Cipher as C
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, json


app = Flask(__name__)
knownServerKey = 12

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'directoryServer.db'),
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


@app.route('/',  methods=['POST'])
def show_files():
    level = getLevel(request.form['token'])
    db = get_db()
    cur = db.execute('select filename from files where level >= ? order by filename asc', [level])
    entryNames = []
    while True:
        row = cur.fetchone()
        if row is None:
            break
        entryNames.append(row["filename"])
    return str(entryNames)


@app.route('/add', methods=['POST'])
def add_entry():
    level = getLevel(request.form['token'])
    fileLevel = request.form['fileLevel']
    if int(level) > int(fileLevel):
        return "You cannot create a file above your level. Your level is " + str(level)
    else:
        db = get_db()
        key = getKey(request.form['token'])
        version = 0
        name = getName(request.form['token'])
        filename = C.decrypt(request.form['filename'], key)
        cur = db.execute('select * from files where filename = ?', [filename])
        row = cur.fetchone()
        if row is not None:
            if row["level"] < level:
                return "You don't have permission to overwrite this file"
            elif row["lock"] is not None:
                if row["lock"] != name:
                    return "This file is locked by " + str(row["lock"])
                else:
                    version = row["version"] + 1
                    lock = row["lock"]
                    lockLevel = row["lockLevel"]
                    db.execute('delete from files where filename = ?', [filename])
                    db.execute('insert into files (filename, body, version, lock, lockLevel, level) values (?, ?, ?, ?, ?, ?)',
                               [filename, C.decrypt(request.form['file'], key), version, lock, lockLevel, fileLevel])
                    db.commit()
                    return json.dumps({"text": "File overwritten", "version": version}, ensure_ascii=True)
            else:
                version = row["version"] + 1
                db.execute('delete from files where filename = ?', [filename])
                db.execute('insert into files (filename, body, version, level) values (?, ?, ?, ?)',
                           [filename, C.decrypt(request.form['file'], key), version, fileLevel])
                db.commit()
                return json.dumps({"text": "File overwritten", "version": version}, ensure_ascii=True)
        else:
            db.execute('insert into files (filename, body, version, level) values (?, ?, ?, ?)',
                       [filename, C.decrypt(request.form['file'], key), version, fileLevel])
            db.commit()
            return json.dumps({"text": "File added", "version": version}, ensure_ascii=True)


@app.route('/get', methods=['POST'])
def get_entry():
    db = get_db()
    level = getLevel(request.form['token'])
    key = getKey(request.form['token'])
    cur = db.execute('select * from files where filename = ? and level >= ?',
                     [C.decrypt(request.form['filename'], key), level])
    row = cur.fetchone()
    if row is None:
        return "File does not exist or you do not have permission to view it"
    elif int(row["version"]) == int(C.decrypt(request.form['curVersion'], key)):
        return "Copy up to date"
    else:
        return json.dumps({"body": row["body"], "version": row["version"]}, ensure_ascii=True)


@app.route('/lock', methods=['POST'])
def lock():
    db = get_db()
    level = getLevel(request.form['token'])
    key = getKey(request.form['token'])
    name = getName(request.form['token'])
    filename = C.decrypt(request.form['filename'], key)
    cur = db.execute('select * from files where filename = ? and level >= ?',
                     [filename, level])
    row = cur.fetchone()
    if row is None:
        return 'File does not exist or you do not have permission to lock it'
    elif row["lock"] is None:
        body = row["body"]
        version = row["version"]
        fileLevel = row["level"]
        db.execute('delete from files where filename = ?', [filename])
        db.execute('insert into files (filename, body, version, lock, lockLevel, level) values (?, ?, ?, ?, ?, ?)',
                   [filename, body, version, name, level, fileLevel])
        db.commit()
        return "File locked"
    else:
        return 'File is already locked by ' + str(row["lock"])


@app.route('/unlock', methods=['POST'])
def unlock():
    db = get_db()
    level = getLevel(request.form['token'])
    key = getKey(request.form['token'])
    name = getName(request.form['token'])
    filename = C.decrypt(request.form['filename'], key)
    cur = db.execute('select * from files where filename = ? and level >= ?',
                     [filename, level])
    row = cur.fetchone()
    if row is None:
        return 'File does not exist or you do not have permission to view it'
    elif row["lock"] is None:
        return "File is not locked"
    elif row["lock"] == name:
        body = row["body"]
        version = row["version"]
        fileLevel = row["level"]
        db.execute('delete from files where filename = ?', [filename])
        db.execute('insert into files (filename, body, version, level) values (?, ?, ?, ?)',
                   [filename, body, version, fileLevel])
        db.commit()
        return "File unlocked"
    elif row["lockLevel"] > level:
        body = row["body"]
        version = row["version"]
        fileLevel = row["level"]
        db.execute('delete from files where filename = ?', [filename])
        db.execute('insert into files (filename, body, version, level) values (?, ?, ?, ?)',
                   [filename, body, version, fileLevel])
        db.commit()
        return "File unlocked"
    else:
        return "You don't have permission to unlock this file"
