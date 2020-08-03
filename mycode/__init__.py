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

    @app.route('/', methods=('GET', 'POST', 'DELETE', 'PATCH'))
    def index():
        dbc = db.get_db()
        if flask.request.method == 'GET':
            user_id = flask.session['user_id']
            goal_list = dbc.execute(
                'SELECT * FROM goals WHERE userid=?', (user_id,)).fetchall()

            if len(goal_list) == 0:
                return json.dumps({'has_goals': False})
            else:
                subgoal_list = dbc.execute(
                    'SELECT * FROM subgoals WHERE userid=?', (user_id,)).fetchall()

                retv = []
                for i in range(len(goal_list)):
                    retv.append(tuple(goal_list[i]))

                if len(subgoal_list) == 0:
                    return json.dumps({'has_goals': True, 'goal_list': retv, 'has_subgoals': False, 'subgoal_list': []})
                else:
                    retv2 = []
                    for i in range(len(subgoal_list)):
                        retv2.append(tuple(subgoal_list[i]))
                    return json.dumps({'has_goals': True, 'goal_list': retv, 'has_subgoals': True, 'subgoal_list': retv2})

        elif flask.request.method == 'DELETE':
            user_id = flask.session['user_id']
            goal_id = flask.request.args.get('id')
            dbc.execute('DELETE FROM goals WHERE goal_id = ?', (goal_id,))
            dbc.execute('DELETE FROM subgoals WHERE goal_id = ?', (goal_id,))
            dbc.commit()

            goal_list = dbc.execute(
                'SELECT * FROM goals WHERE userid=?', (user_id,)).fetchall()

            if len(goal_list) == 0:
                return json.dumps({'status': 'success', 'has_goals': False, 'goal_list': []})
            else:
                subgoal_list = dbc.execute(
                    'SELECT * FROM subgoals WHERE userid=?', (user_id,)).fetchall()

                retv = []
                for i in range(len(goal_list)):
                    retv.append(tuple(goal_list[i]))

                if len(subgoal_list) == 0:
                    return json.dumps({'status': 'success', 'has_goals': True, 'goal_list': retv, 'has_subgoals': False, 'subgoal_list': []})
                else:
                    retv2 = []
                    for i in range(len(subgoal_list)):
                        retv2.append(tuple(subgoal_list[i]))
                    return json.dumps({'status': 'success', 'has_goals': True, 'goal_list': retv, 'has_subgoals': True, 'subgoal_list': retv2})

        elif flask.request.method == 'PATCH':
            if flask.request.form['type'] == 'status':
                user_id = flask.session['user_id']
                goal_id = flask.request.form['id']
                status = flask.request.form['status']
                dbc.execute(
                    'UPDATE goals SET status = ? WHERE goal_id = ?', (status, goal_id))
                if status == "1":
                    dbc.execute(
                        'UPDATE subgoals SET status = 1 WHERE goal_id = ?', (goal_id,))

                dbc.commit()

                return json.dumps({'status': 'success'})

            elif flask.request.form['type'] == 'title':
                user_id = flask.session['user_id']
                goal_id = flask.request.form['id']
                new_title = flask.request.form['value'].lower()
                old_title = dbc.execute(
                    "SELECT * FROM goals WHERE goal_id= ?", (goal_id,)).fetchone()['title']
                new_deadline = flask.request.form['deadline']

                if (dbc.execute('SELECT * FROM goals WHERE title= ? AND userid = ?', (new_title, user_id)).fetchone() is not None) and new_title != old_title:
                    return json.dumps({'status': 'error', 'message': 'Duplicate titles not allowed!'})
                else:
                    if new_deadline == "none":
                        dbc.execute(
                            'UPDATE goals set title = ? WHERE goal_id = ?', (new_title, goal_id))
                    else:
                        dbc.execute(
                            'UPDATE goals set title = ?, deadline = ? WHERE goal_id = ?', (new_title, new_deadline, goal_id))
                    dbc.commit()

                    return json.dumps({'status': 'success'})

        else:
            user_id = flask.session['user_id']
            goal_title = flask.request.form['goal'].lower()
            deadline = flask.request.form['deadline']
            if dbc.execute('SELECT * FROM goals WHERE title= ? AND userid = ?', (goal_title, user_id)).fetchone() is not None:
                return json.dumps({'status': 'error', 'message': 'Goal already exists!'})
            else:
                dbc.execute('INSERT INTO goals (userid, title, deadline) VALUES(?, ?, ?)',
                            (user_id, goal_title, deadline))
                dbc.commit()
                return json.dumps({'status': "Goal Added"})

    @app.route('/subgoals', methods=('GET', 'POST', 'DELETE', 'PATCH'))
    def subgoals():
        dbc = db.get_db()
        user_id = flask.session['user_id']

        if flask.request.method == 'GET':
            sub_goals_row = dbc.execute(
                'SELECT * FROM subgoals WHERE userid = ?', (user_id,)).fetchall()
            if len(sub_goals_row) == 0:
                return json.dumps({'subgoals': [(-1, 'This course has no sub-goals', -1)], 'status': 0})
            else:
                sub_goals_tuples = []
                for i in range(len(sub_goals_row)):
                    sub_goals_tuples.append(tuple(sub_goals_row[i]))
                return json.dumps({'subgoals': sub_goals_tuples})

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
                    'INSERT INTO subgoals(userid, goal_id, title, status) VALUES (?, ?, ?, ?)', (user_id, goal_id, title, 0))
                dbc.commit()

                sub_goals_row = dbc.execute(
                    'SELECT * FROM subgoals WHERE userid = ?', (user_id,)).fetchall()
                sub_goals_tuples = []
                for i in range(len(sub_goals_row)):
                    sub_goals_tuples.append(tuple(sub_goals_row[i]))
                return json.dumps({'status': 'success', 'subgoal_list': sub_goals_tuples})

        elif flask.request.method == 'DELETE':
            s_id = flask.request.args.get('id')
            dbc.execute('DELETE FROM subgoals WHERE sgoalid = ?', (s_id,))
            dbc.commit()
            return json.dumps({'status': 'success'})

        elif flask.request.method == 'PATCH':
            s_id = flask.request.form['id']
            status = flask.request.form['status']
            dbc.execute(
                'UPDATE subgoals SET status = ? WHERE sgoalid = ?', (status, s_id))
            dbc.commit()
            return json.dumps({'status': 'success'})

    return app
