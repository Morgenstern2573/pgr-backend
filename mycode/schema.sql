DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS subcourses;

CREATE TABLE users(
    'id' INTEGER PRIMARY KEY AUTOINCREMENT,
    'username' TEXT UNIQUE NOT NULL,
    'password' TEXT NOT NULL
);

CREATE TABLE  courses(
    'userid' INTEGER,
    'title' TEXT NOT NULL,
    'code' TEXT NOT NULL,
    'course_id' INTEGER PRIMARY KEY AUTOINCREMENT
);

CREATE TABLE subcourses(
    'course_id' INTEGER,
    'scourseid' INTEGER PRIMARY KEY AUTOINCREMENT,
    'title' TEXT UNIQUE NOT NULL,
    'status' INTEGER
);