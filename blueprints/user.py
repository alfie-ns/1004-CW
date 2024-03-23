# This file contains the user blueprint, which is used to handle all user related requests.

import sqlite3
from blueprints.calculations import calculate_calorific_needs, calculate_bmr, calculate_ideal_body_weight, calculate_macronutrient_split, calculate_tdee, calculate_bmi, calculate_body_fat_percentage
from blueprints.get_response import goal_descriptions, session
from flask import Blueprint, redirect, render_template
from flask_login import current_user, login_required, UserMixin

# Blueprint configuration
user = Blueprint('user', __name__, template_folder='templates', static_folder='static', static_url_path='/static')

# User class 
class User(UserMixin):
    def __init__(self, id, username, email, password, gender, age, height, weight, goal, determination_level, activity_level, bmr_type, body_fat_percentage, workout_plans=None): 
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.gender = gender
        self.age = age
        self.height = height
        self.weight = weight
        self.goal = goal
        self.determination_level = determination_level
        self.activity_level = activity_level
        self.bmr_type = bmr_type
        self.body_fat_percentage = body_fat_percentage
        self.workout_plans = workout_plans or []
        self.detailed_goal = goal_descriptions.get(goal, "Default description")

    def is_anonymous(self):
        return False
    def is_active(self):
        return True
    def get_id(self):
        return self.id
    def get_username(self):
        return self.username
    def is_authenticated(self):
        return True
    def get_formatted_goal(self):
        return self.goal.replace('_', ' ').title()
    def get_formatted_activity_level(self):
        return self.activity_level.replace('_', ' ').title()
    def get_formatted_age(self):    
        return str(self.age) + ' years'
    def get_formatted_weight(self):
        return str(round(self.weight)) + ' kg'
    def get_formatted_height(self):
        return str(round(self.height)) + ' cm'     
    def get_calorific_needs(self):
        daily_calorific_needs = calculate_calorific_needs()
        return daily_calorific_needs
    def get_bmr(self):
        bmr = calculate_bmr()
        return bmr
    def get_ideal_body(self):
        ideal_body = calculate_ideal_body_weight()
        return ideal_body
    def get_macros_split(self):
        macros_split = calculate_macronutrient_split()
        return macros_split
    def get_tdee(self):
        tdee = calculate_tdee()
        return tdee
    def get_bmi(self):
        bmi = calculate_bmi()
        return bmi
    def get_body_fat(self):
        body_fat_percentage = calculate_body_fat_percentage()
        if body_fat_percentage == None:
            return "No body fat percentage set"
        else:
            return str(body_fat_percentage) + '%'
    def get_determination_level(self):
        determination_level = self.determination_level.replace('_', ' ').title()
        return determination_level
    def get_formatted_gender(self):
        if self.gender == 'male':
            return "Male"
        elif self.gender == 'female':
            return "Female"  
        else:
            ValueError(f"Unknown Gender: {self.gender}")
    def get_goal_timeframe(self):
        determination_level_timeframes = {
            'casual': 12,
            'determined': 6,
            'very_determined': 3
        }
        return determination_level_timeframes.get(self.determination_level, "No timeframe set") 

    
def loadUserObject(user_id):
    # Load user object from the database
    conn = sqlite3.connect('database.db')
    curs = conn.cursor()
    curs.execute("SELECT id, username, email, password, gender, age, height, weight, goal, determination_level, activity_level, bmr_type, body_fat_percentage FROM users WHERE id = (?)", [user_id])
    user_data = curs.fetchone()
    conn.close()

    if user_data:
        return User(*user_data)
    else:
        return None

    
@user.route('/delete_account', methods=['POST', 'GET'])
def delete_account():
    # Delete user from the database
    conn = sqlite3.connect('database.db')
    curs = conn.cursor()
    curs.execute("DELETE FROM users WHERE id = (?)", [current_user.id])
    conn.commit()
    conn.close()
    return redirect('/')


@user.route('/clear_conversation', methods=['POST', 'GET'])
@login_required
def clear_all():
    # Delete all messages from the database
    conn = sqlite3.connect('database.db')
    curs = conn.cursor()
    curs.execute("DELETE FROM conversations WHERE user_id = ?", (current_user.id,)) 
    conn.commit()
    conn.close()

    session.pop("conversation", default=None)

    return redirect(f'/main/{current_user.id}')

@user.route("/account.html")
@login_required
def account_redirect():
    # Retrieve initial_plan from the database
    conn = sqlite3.connect('database.db')
    curs = conn.cursor()
    curs.execute("SELECT initial_plan FROM users WHERE id = ?", (current_user.id,))
    initial_plan = curs.fetchone()[0]
    conn.close()
    return render_template('/account.html', initial_plan=initial_plan)


