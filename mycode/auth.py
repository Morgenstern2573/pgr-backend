import functools
import json

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('POST',))
def register():
    con = get_db()
    if request.method == 'POST':
        username = request.form['username'].lower().lstrip()
        password = request.form['password'].lstrip()
        confirm = request.form['confirm'].lstrip()

        if username is None or password is None or username == " " or username == "" or password == " " or password == "":
            return json.dumps({"status": "error", "message": 'Username or password not given'})
        elif password != confirm:
            return json.dumps({"status": "error", "message": 'password doesn\'t match confirmation password'})
        elif con.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone() is not None:
            return json.dumps({"status": "error", "message": 'username already registered'})
        else:
            con.execute('INSERT INTO users(username, password) VALUES(?, ?)',
                        (username, generate_password_hash(password)))
            con.commit()
            session['user_id'] = con.execute(
                'SELECT * FROM users WHERE username=?', (username,)).fetchone()['id']
            return json.dumps({"status": "registered"})


@bp.route('/login', methods=('POST',))
def login():
    con = get_db()
    if request.method == 'POST':
        username = request.form['username'].lower().lstrip()
        password = request.form['password'].lstrip()
        user = con.execute(
            'SELECT * FROM users WHERE username=?', (username,)).fetchone()
        if username is None or password is None or username == " " or username == "" or password == " " or password == "":
            return json.dumps({"status": "error", "message": 'Username or password not given'})
        elif user is None:
            return json.dumps({"status": "error", "message": 'Username is not registered'})
        elif not check_password_hash(user['password'], password):
            return json.dumps({"status": "error", "message": 'Incorrect Passsword!'})
        else:
            session['user_id'] = user['id']
            return json.dumps({"status": "logged in"})


@bp.route('/logout', methods=('GET',))
def logout():
    if 'user_id' in session:
        session.pop('user_id')
    return json.dumps({"status": "logged out"})


@bp.route('/user-status', methods=('GET',))
def status():
    if 'user_id' in session:
        return json.dumps("User logged in")
    return json.dumps("User not logged in")
