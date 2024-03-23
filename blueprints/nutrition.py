from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from blueprints.get_response import get_user_info, get_system_message 
from blueprints.calculations import calculate_calorific_needs
from blueprints.get_response import get_goal_timeframe
from blueprints.prompts import goal_descriptions
import openai, sqlite3

# This blueprint handles the nutirition and dieting pages

nutrition = Blueprint('nutrition', __name__, template_folder='templates')

@nutrition.route('/nutrition_generate')  
@login_required
def generate_meal_plan():
    print("ENTERED GENERATE MEAL PLAN FUNCTION")

    user_data = get_user_info() # Loads the user info from the database
    daily_calorific_needs = calculate_calorific_needs()
    detailed_goal = goal_descriptions.get(user_data[5])
    goal_timeframe = get_goal_timeframe(user_data[6])
    system_message = get_system_message()
    detailed_goal = goal_descriptions.get(user_data[5])

    prompt = f"""   I have a user with the following details: {system_message}.
                    I need to create a healthy weekly meal plan to help them achieve their goal which is to {detailed_goal},
                    while meeting their daily caloric needs. Please suggest a weekly meal plan."""

    response = openai.ChatCompletion.create(
      model="gpt-4-1106-preview",
      messages=[
          {"role": "system", "content": "You are a helpful assistant."},
          {"role": "user", "content": prompt}
      ]
    )

    meal_plan = response['choices'][0]['message']['content']  # Extracting the meal plan from the response

    return render_template('nutrition_plans.html', meal_plan=meal_plan)


# This function renders the nutrition page
@nutrition.route('/nutrition') 
@login_required
def nutrition_page():
    print("ENTERED NUTRITION PAGE FUNCTION")

    return render_template('nutrition_plans.html')
