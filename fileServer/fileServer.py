import os
import errno
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
    SECRET_KEY='ServerKEY'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def getLevel(token):
    info = json.loads(C.decrypt(token, knownServerKey))
    return info["level"]


def getKey(token):
    info = json.loads(C.decrypt(token, knownServerKey))
    return info["key"]


def getName(token):
    info = json.loads(C.decrypt(token, knownServerKey))
    return info["username"]


@app.route('/add', methods=['POST'])
def add_entry():
    key = getKey(request.form['token'])
    body = C.decrypt(request.form['file'], key)
    filename = C.decrypt(request.form['filename'], key)
    path = 'files/' + filename
    try:
        if not os.path.exists(os.path.dirname(path)):
            try:
                os.makedirs(os.path.dirname(path))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
        f = open(path, 'w')
        f.write(body)
        return "file written"
    except IOError:
        return"Error writing file"


@app.route('/get', methods=['POST'])
def get_entry():
    return "get pls"


#  C.decrypt(request.form['file'], key),
