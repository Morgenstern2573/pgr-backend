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
                             'https://pgrtracker.vercel.app/')
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    @app.route('/', methods=('GET', 'POST'))
    def index():
        dbc = db.get_db()
        if flask.request.method == 'GET':
            user_id = flask.session['user_id']
            course_list = dbc.execute(
                'SELECT * FROM courses WHERE userid=?', (user_id,)).fetchall()
            if len(course_list) == 0:
                course_list = json.dumps(
                    [[user_id, "User has no courses", "-1", -1]])
                return course_list
            else:
                retv = []
                for i in range(len(course_list)):
                    retv.append(tuple(course_list[i]))
                return json.dumps(retv)

        else:
            user_id = flask.session['user_id']
            course_title = flask.request.form['course'].lower()
            course_code = flask.request.form['code'].lower()
            if dbc.execute('SELECT * FROM courses WHERE title= ? AND userid = ?', (course_title, user_id)).fetchone() is not None:
                return json.dumps({'status': 'error', 'message': 'Course already exists!'})
            else:
                dbc.execute('INSERT INTO courses (userid, title, code) VALUES(?, ?, ?)',
                            (user_id, course_title, course_code))
                dbc.commit()
                return json.dumps({'status': "Course Added"})

    @app.route('/course', methods=('GET', 'POST', 'PATCH', 'DELETE'))
    def course():
        dbc = db.get_db()
        user_id = flask.session['user_id']
        if flask.request.method == 'GET':
            course_id = flask.request.args.get('id')
            course_name = dbc.execute(
                'SELECT * FROM courses WHERE course_id = ?', (course_id,)).fetchone()['title']
            sub_courses_row = dbc.execute(
                'SELECT * FROM subcourses WHERE course_id = ?', (course_id)).fetchall()
            if len(sub_courses_row) == 0:
                return json.dumps({'course': course_name, 'subcourses': [(course_id, -1, 'User has no sub-courses', -1)]})
            else:
                sub_courses_tuples = []
                for i in range(len(sub_courses_row)):
                    sub_courses_tuples.append(tuple(sub_courses_row[i]))
                return json.dumps({'course': course_name, 'subcourses': sub_courses_tuples})
        elif flask.request.method == 'POST':
            title = flask.request.form['title'].lower().lstrip()
            course_id = flask.request.form['id'].lstrip()
            if title is None or course_id is None:
                return json.dumps({'status': 'error', 'message': 'Title not given'})
            elif title == "" or course_id == "":
                return json.dumps({'status': 'error', 'message': 'Title cannot be empty or the space character'})
            elif dbc.execute('SELECT * FROM subcourses WHERE title = ? AND course_id = ?', (title, course_id)).fetchone() is not None:
                return json.dumps({'status': 'error', 'message': 'Duplicate Sub Courses not allowed'})
            else:
                dbc.execute(
                    'INSERT INTO subcourses(course_id, title, status) VALUES (?, ?, ?)', (course_id, title, 0))
                dbc.commit()
                return json.dumps({'status': 'success'})
        elif flask.request.method == 'DELETE':
            s_id = flask.request.args.get('id')
            dbc.execute('DELETE FROM subcourses WHERE scourseid = ?', (s_id,))
            dbc.commit()
            return json.dumps({'status': 'success'})

    @app.route('/scourse', methods=('POST',))
    def scourse():
        dbc = db.get_db()
        s_id = flask.request.form['id']
        status = flask.request.form['status']
        print("The id is ", s_id)
        print("The status is", status)
        dbc.execute(
            'UPDATE subcourses SET status = ? WHERE scourseid = ?', (status, s_id))
        dbc.commit()
        return json.dumps({'status': 'success'})

    return app
