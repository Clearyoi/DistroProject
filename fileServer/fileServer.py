import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash


app = Flask(__name__)

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


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_files():
    db = get_db()
    cur = db.execute('select filename from files order by filename asc')
    entryNames = []
    while True:
        row = cur.fetchone()
        if row is None:
            break
        entryNames.append(row["filename"])
    return str(entryNames)


@app.route('/setKey')
def set_key():
    return "success"


@app.route('/add', methods=['POST'])
def add_entry():
    # if not session.get('logged_in'):
    #     abort(401)
    db = get_db()
    db.execute('delete from files where filename = ?', [request.form['filename']])
    db.execute('insert into files (filename, body, version, lock) values (?, ?, 0, 0)',
               [request.form['filename'], request.form['file']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_files'))


@app.route('/get', methods=['POST'])
def get_entry():
    # if not session.get('logged_in'):
    #     abort(401)
    db = get_db()
    cur = db.execute('select body from files where filename = ?', [request.form['filename']])
    row = cur.fetchone()
    if row is None:
        return "Invalid name"
    return str(row["body"])


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_files'))
    return error


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_files'))
