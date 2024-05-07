#Models the entire application and contains the main functions.

# This file is the main 

# General
import openai, os, secrets, sqlite3
# Environment variables
from dotenv import load_dotenv
# Flask
from flask import Flask, app, g
from flask_login import LoginManager, current_user
from flask_mail import Mail
# Blueprints
from blueprints.login import login
from blueprints.register import register
from blueprints.plans import plans
from blueprints.user import user, loadUserObject
from blueprints.get_response import get_response
from blueprints.routes import routes
from blueprints.prompts import prompts
from blueprints.calculations import calculations
from blueprints.nutrition import nutrition
from blueprints.get_youtube import youtube
from blueprints.function_call import function_call_descriptions


load_dotenv(".env") # Loads the .env file

async_mode = None # Sets the async mode to None


# App configuration
app = Flask(__name__) # Creates the Flask app instance
app.debug = True # Allows for debugging
app.secret_key = secrets.token_hex(16) # Creates a secret key for the session

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com' # Sets the SMTP server
app.config['MAIL_PORT'] = 587 # Sets the SMTP port
app.config['MAIL_USE_TLS'] = True # Sets the TLS protocol
app.config['MAIL_USERNAME'] = 'alfienurse@gmail.com' # Sets the email address
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD') # Sets the email password
app.config['MAIL_DEFAULT_SENDER'] = 'alfiemnurse@gmail.com' # Sets the default sender
mail = Mail(app) # Needed also in regisiter blueprint to work ?? [ ]


# Login manager configuration
login_manager = LoginManager() # Creates a login manager instance
login_manager.login_view = 'login.loginPage' # Sets the login view to the login blueprint function loginPage
login_manager.init_app(app) # Initialises the login manager with the app instance


# OpenAI API configuration
openai.api_key = os.getenv("OPENAI_API_KEY") # Sets the OpenAI API key



#This function retrieves the user from the database using the provided user_id, essential for managing user sessions.
@login_manager.user_loader # Decorator for the user_loader function
def load_user(user_id):
    user_data = loadUserObject(user_id) # Loads the user data from the database
    return user_data # Returns the user data    

    


# This decorator ensures that the following function runs before each request in the Flask application
@app.before_request 
def before_request():
    if current_user.is_authenticated:  # Checks if the user is authenticated 
        conn = sqlite3.connect('database.db') # Connect to the SQLite database
        curs = conn.cursor() # Create a cursor object to execute SQL commands
        curs.execute("SELECT username, gender, age, height, weight, goal FROM users WHERE id = (?)", [current_user.id]) # Fetch the user data by user ID
        g.user_data = curs.fetchone() # Assign the fetched user data to a global object "g" which is unique for each request context
        conn.close() # Close the connection to the SQLite database


# Registering the blueprints
app.register_blueprint(login)
app.register_blueprint(register)
app.register_blueprint(plans)
app.register_blueprint(user)
app.register_blueprint(get_response)
app.register_blueprint(routes)
app.register_blueprint(prompts)
app.register_blueprint(calculations)
app.register_blueprint(nutrition)
app.register_blueprint(youtube)
app.register_blueprint(function_call_descriptions)

# This conditional ensures that the app runs only when the app.py file is run directly
if __name__ == "__main__":
    app.run()


    








