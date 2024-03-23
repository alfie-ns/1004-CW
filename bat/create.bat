@echo off

REM Create the database

cd ..

DEL database.db

ECHO CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, email TEXT, password TEXT, gender TEXT, age INTEGER, height REAL, weight REAL, waist REAL, neck REAL, hip REAL, head REAL, goal TEXT, determination_level TEXT, activity_level TEXT, bmr_type TEXT, body_fat_percentage INTEGER, initial_plan TEXT, report TEXT, bmr FLOAT); | sqlite3 database.db
ECHO CREATE TABLE conversations (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, conversation TEXT, FOREIGN KEY (user_id) REFERENCES users (id)); | sqlite3 database.db
ECHO CREATE TABLE workout_plans (id INTEGER PRIMARY KEY, user_id INTEGER, fitness_level TEXT, goal TEXT, exercises TEXT, FOREIGN KEY (user_id) REFERENCES users (id)); | sqlite3 database.db
ECHO CREATE TABLE goals (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, short_term_goal TEXT, long_term_goal TEXT, progress TEXT, FOREIGN KEY (user_id) REFERENCES users (id)); | sqlite3 database.db
ECHO CREATE TABLE function_calls (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, function_name TEXT, function_arguments TEXT, report TEXT, function_response TEXT, assistant_message TEXT, FOREIGN KEY(user_id) REFERENCES users(id)); | sqlite3 database.db
ECHO CREATE TABLE meal_plans (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, meal_plans TEXT, FOREIGN KEY (user_id) REFERENCES users (id)); | sqlite3 database.db

ECHO INSERT INTO users (username, email, password, gender, age, height, weight, goal, determination_level, activity_level, bmr_type, body_fat_percentage, initial_plan, report) VALUES ('Alfie', '', 'y', 'male', 20, 175, 75, 'six_pack', 'determined', 'sedentary', 'mifflin_st_jeor', '', '', ''); | sqlite3 database.db
ECHO INSERT INTO users (username, email, password, gender, age, height, weight, goal, determination_level, activity_level, bmr_type, body_fat_percentage, initial_plan, report) VALUES ('a', '', 'b', 'male', 55, 190, 135, 'lose_weight', 'casual', 'moderately_active', 'katch_mcardle', 30 , '', ''); | sqlite3 database.db

ECHO .sch | sqlite3 database.db
ECHO .sch | sqlite3 database.db
