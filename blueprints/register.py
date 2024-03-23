# This file contains the register blueprint, which handles the registration of new users

from flask import Flask, render_template, request, Blueprint, jsonify
#from werkzeug.security import generate_password_hash
import sqlite3, re
from flask_mail import Mail, Message

app = Flask(__name__)
mail = Mail()
register = Blueprint("register", __name__, static_folder="static", template_folder="templates\n")


# Renders register page
@register.route("/register.html")
def register_view():
    return render_template('register.html')

# Process' the register form, sends user to the process register page if successful, otherwise sends user to the failed register page
@register.route('/process-register', methods=['POST'])
def process_register(): #request.form.get() gets "name" of input field
    print("Entered process_register\n")

    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    gender = request.form.get('gender')
    age = request.form.get('age')
    #------------------------------#
    #ADVANCED
    waist = request.form.get('waist')
    neck = request.form.get('neck')
    hip = request.form.get('hip')
    #------------------------------#
    goal = request.form.get('goal')
    determination_level = request.form.get('determination_level')
    activity_level = request.form.get('activity_level')
    bmr_type = request.form.get('bmr_type')
    if bmr_type != 'katch_mcardle':
        body_fat_percentage = None
    else:
        body_fat_percentage = request.form.get('body_fat_percentage')
        
    # Process height
    height_unit = request.form.get('height_unit')
    if height_unit == 'ft':
        height_ft = request.form.get('height_ft')
        height_in = request.form.get('height_in')
        if height_ft is not None and height_in is not None and height_ft.isdigit() and height_in.isdigit():
            height = float(height_ft) * 30.48 + float(height_in) * 2.54
        else:
            height = None
    elif height_unit == 'cm': 
        height_cm = request.form.get('height') # General height is in centermetres
        if height_cm is not None and height_cm.isdigit(): 
            height = float(height_cm)
        else:
            height = None

    # Process weight
    weight = request.form.get('weight')
    weight_unit = request.form.get('weight_unit')
    if weight is not None and weight.isdigit() and weight_unit == "lb":
        weight = float(weight) * 0.45359237  # conversion ratio from lbs to kg

    print(f'Converted height: {height}')
    print(f'Converted weight: {weight}')
    password_meets_requirements = bool(re.search(r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_\-+=\[\]{};:\\|,.<>\/?])(?=.*[a-z]).{8,}$', password))
    print(f"Form values: {username}, {email}, {gender}, {age}, {height}, {weight}, {waist}, {neck}, {hip}, {goal}, {determination_level}, {activity_level}, {height_unit}, {weight_unit}, {bmr_type}")
    print(f"Password meets requirements: {password_meets_requirements}")


    # If all form fields are filled out and the password meets the requirements, add the user to the database, otherwise send the user to the failed register page
    if all([username, email, password, gender, age, height, weight, goal, determination_level, activity_level, height_unit, weight_unit, bmr_type]) and re.search(r"^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_\-+=\[\]{};:\\|,.<>\/?])(?=.*[a-z]).{8,}$", password):
        print('All form fields are filled and password requirements are met')
        try:
            conn = sqlite3.connect('database.db')
            curs = conn.cursor()
            print(f"BFP: {body_fat_percentage}")
            curs.execute("INSERT INTO users (username, email, password, gender, age, height, weight, waist, neck, hip, goal, determination_level, activity_level, bmr_type, body_fat_percentage, initial_plan) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (username, email, password, gender, age, height, weight, waist, neck, hip, goal, determination_level, activity_level, bmr_type, body_fat_percentage, ''))
            conn.commit()
            conn.close()

            # Confirmation email testing
            msg = Message("Welcome to VPT!", recipients=[email])
            msg.body = f"Thank you for registering, {username}! We are excited to have you on board."
            mail.send(msg)

            return render_template('process-register.html')
        
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return render_template('failed-register.html')
        except Exception as e:
            print(f"Exception in _query: {e}")
            return render_template('failed-register.html')
    else:
        print('Not all form fields are filled or password requirements are not met')
        return render_template('failed-register.html')

# Checks if username is taken
@register.route('/check-username', methods=['POST'])
def check_username():
    username = request.json.get('username')

    # Check the username availability
    try:
        conn = sqlite3.connect('database.db')
        curs = conn.cursor()
        curs.execute("SELECT * FROM users WHERE username = ?", (username,))
        taken = curs.fetchone()
        is_available = taken is None
        conn.close()

        response = {'available': is_available}
        return jsonify(response)
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({'available': None})
    except Exception as e:
        print(f"Exception in _query: {e}")
        return jsonify({'available': None})
