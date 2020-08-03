DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS goals;
DROP TABLE IF EXISTS subgoals;

CREATE TABLE users(
    'id' INTEGER PRIMARY KEY,
    'username' TEXT UNIQUE NOT NULL,
    'password' TEXT NOT NULL
);

CREATE TABLE  goals(
    'id' BIGINT PRIMARY KEY,
    'parent_id' BIGINT NOT NULL DEFAULT 0,
    'user_id' INTEGER,
    'title' TEXT NOT NULL,
    'status' INTEGER DEFAULT 0,
    'deadline' TEXT NOT NULL
);

-- CREATE TABLE subgoals(
--     'userid' INTEGER,
--     'goal_id' INTEGER,
--     'sgoalid' INTEGER PRIMARY KEY,
--     'title' TEXT NOT NULL,
--     'status' INTEGER
-- );