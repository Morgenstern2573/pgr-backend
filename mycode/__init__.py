from . import db, auth
import json
import os
import flask
from flask import Flask


def create_app():
    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'bkr.sqlite'),
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    app.register_blueprint(auth.bp)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin',
                             'https://pgrtracker.vercel.app')
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    @app.route('/', methods=('GET', 'POST', 'DELETE'))
    def index():
        dbc = db.get_db()
        if flask.request.method == 'GET':
            user_id = flask.session['user_id']
            goal_list = dbc.execute(
                'SELECT * FROM goals WHERE userid=?', (user_id,)).fetchall()
            if len(goal_list) == 0:
                goal_list = json.dumps(
                    [[user_id, "User has no goals", -1, -1]])
                return goal_list
            else:
                retv = []
                for i in range(len(goal_list)):
                    retv.append(tuple(goal_list[i]))
                return json.dumps(retv)
        elif flask.request.method == 'DELETE':
            course_id = flask.request.args.get('id')
            dbc.execute('DELETE FROM goals WHERE goal_id = ?', (course_id,))
            dbc.execute('DELETE FROM subgoals WHERE goal_id = ?', (course_id,))
            dbc.commit()
            return json.dumps({'status': 'success'})
        else:
            user_id = flask.session['user_id']
            goal_title = flask.request.form['goal'].lower()
            if dbc.execute('SELECT * FROM goals WHERE title= ? AND userid = ?', (goal_title, user_id)).fetchone() is not None:
                return json.dumps({'status': 'error', 'message': 'Goal already exists!'})
            else:
                dbc.execute('INSERT INTO goals (userid, title) VALUES(?, ?)',
                            (user_id, goal_title))
                dbc.commit()
                return json.dumps({'status': "Goal Added"})

    @app.route('/goal', methods=('GET', 'POST', 'PATCH', 'DELETE'))
    def goal():
        dbc = db.get_db()
        user_id = flask.session['user_id']
        if flask.request.method == 'GET':
            goal_id = flask.request.args.get('id')
            goal = dbc.execute(
                'SELECT * FROM goals WHERE goal_id = ?', (goal_id,)).fetchone()
            sub_goals_row = dbc.execute(
                'SELECT * FROM subgoals WHERE goal_id = ?', (goal_id,)).fetchall()
            if len(sub_goals_row) == 0:
                return json.dumps({'goal': goal['title'], 'subgoals': [(goal_id, -1, 'User has no sub-goals', -1)], 'status': 0})
            else:
                sub_goals_tuples = []
                for i in range(len(sub_goals_row)):
                    sub_goals_tuples.append(tuple(sub_goals_row[i]))
                return json.dumps({'goal': goal['title'], 'subgoals': sub_goals_tuples, 'status': goal['status']})
        elif flask.request.method == 'POST':
            title = flask.request.form['title'].lower().lstrip()
            goal_id = flask.request.form['id'].lstrip()
            if title is None or goal_id is None:
                return json.dumps({'status': 'error', 'message': 'Title not given'})
            elif title == "" or goal_id == "":
                return json.dumps({'status': 'error', 'message': 'Title cannot be empty or the space character'})
            elif dbc.execute('SELECT * FROM subgoals WHERE title = ? AND goal_id = ?', (title, goal_id)).fetchone() is not None:
                return json.dumps({'status': 'error', 'message': 'Duplicate Sub goals not allowed'})
            else:
                dbc.execute(
                    'INSERT INTO subgoals(goal_id, title, status) VALUES (?, ?, ?)', (goal_id, title, 0))
                dbc.commit()
                return json.dumps({'status': 'success'})
        elif flask.request.method == 'DELETE':
            s_id = flask.request.args.get('id')
            dbc.execute('DELETE FROM subgoals WHERE sgoalid = ?', (s_id,))
            dbc.commit()
            return json.dumps({'status': 'success'})
        elif flask.request.method == 'PATCH':
            goal_id = flask.request.form['id']
            status = flask.request.form['status']
            print(goal_id, status)
            dbc.execute(
                'UPDATE goals SET status = ? WHERE goal_id = ?', (status, goal_id))
            dbc.commit()
            return json.dumps({'status': 'success'})

    @app.route('/scourse', methods=('POST',))
    def scourse():
        dbc = db.get_db()
        s_id = flask.request.form['id']
        status = flask.request.form['status']
        dbc.execute(
            'UPDATE subgoals SET status = ? WHERE sgoalid = ?', (status, s_id))
        dbc.commit()
        return json.dumps({'status': 'success'})

    return app
