from flask import Blueprint, render_template, request
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
import sqlite3
from blueprints.user import loadUserObject
from flask import session, redirect
from typing import List, Dict, Tuple, Union

login = Blueprint('login', __name__, template_folder="templates")
login_manager = LoginManager()

# If user is unauthorized, redirect to the login page
@login_manager.unauthorized_handler
def unauthorized():
    return redirect('/')

# Renders the login page
@login.route('/')
@login.route('/login.html')
def loginPage():
    logout_user()
    return render_template('login.html')

# Processes the login form, then sends the user to their account page
@login.route("/process-login", methods=['POST', 'GET'])
def login_process():
    username = request.form.get('username')
    password = request.form.get('password')

    # Check if the user exists in the database
    conn = sqlite3.connect('database.db')
    curs = conn.cursor()  
    curs.execute("SELECT * FROM users WHERE username = (?)", [username])

    rec = curs.fetchone()
    conn.close()

    print(f"User record from database: {rec}")

    # If the user does not exist, return the failed login page
    if rec is None:
        return render_template('/failed-login.html')
    
    # Convert the tuple to a list
    user = list(rec)
    userId = user[0]
    userObj = loadUserObject(userId)

    print(f"User Object: {userObj}, Entered Password: {password}, Stored Password: {userObj.password}")


    # If the user exists, check if the password is correct, then log them in
    if userObj.username == username and userObj.password == password:
        
        #login_user(userObj)

        login_result = login_user(userObj)
        print(f"Login result: {login_result}")

        # Ensuring the conversation is in the session
        if "conversation" not in session:
            session["conversation"] = []

        if session["conversation"] == None:
            session["conversation"] = []


        # MJN - redirect to the account page
        return redirect('account.html')
        # MJN return render_template(f'/account.html', initial_plan=initial_plan)
    
    # If the password is incorrect, return the failed login page
    else:
        return render_template('/failed-login.html')

# Renders the failed login page   
@login.route("/failed-login.html")
def failed_login():
    return render_template('failed-login.html')

# Renders account page with the user's initial plan
@login.route("/account.html")
@login_required
def profile():

    print("FILE: login.py", "ROUTE: /account.html", "FUNC: profile\n")

    # Ensuring the conversation is in the session
    if "conversation" not in session:
        session["conversation"] = []
    elif session["conversation"] == None:
        session["conversation"] = []

    
    

     
    # Render account page with nessesary data for Jinja 
    return render_template('account.html', userObj=current_user, daily_calorific_needs=current_user.get_calorific_needs(), bmr=current_user.get_bmr(),
                            bmi = current_user.get_bmi(), ideal_body=current_user.get_ideal_body(), macros_split = current_user.get_macros_split(),
                            tdee = current_user.get_tdee(), formatted_goal=current_user.get_formatted_goal(), formatted_activity_level=current_user.get_formatted_activity_level(),
                            formatted_height=current_user.get_formatted_height(), formatted_weight=current_user.get_formatted_weight(), formatted_age=current_user.get_formatted_age(),)

# Logs the user out, returns them to base page     
@login.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')