DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS goals;
DROP TABLE IF EXISTS subgoals;

CREATE TABLE users(
    'id' INTEGER PRIMARY KEY AUTOINCREMENT,
    'username' TEXT UNIQUE NOT NULL,
    'password' TEXT NOT NULL
);

CREATE TABLE  goals(
    'userid' INTEGER,
    'title' TEXT NOT NULL,
    'goal_id' INTEGER PRIMARY KEY AUTOINCREMENT,
    'status' INTEGER DEFAULT 0
);

CREATE TABLE subgoals(
    'goal_id' INTEGER,
    'sgoalid' INTEGER PRIMARY KEY AUTOINCREMENT,
    'title' TEXT NOT NULL,
    'status' INTEGER
);