from flask import redirect, request, flash, url_for, Blueprint
from flask_login import current_user, login_required
from typing import List, Any
import sqlite3

plans = Blueprint('plans', __name__, template_folder='templates')

# Creates workout plan, then redirects to the main page
@plans.route('/create_workout_plan', methods=['POST'])
@login_required
def create_workout_plan() -> Any:
    # Get the form data
    fitness_level = request.form.get('fitness_level')
    goal = request.form.get('goal')
    preferred_exercises = request.form.get('preferred_exercises')

    # Generates workout plan with form data
    workout_plan = generate_workout_plan(fitness_level, goal, preferred_exercises.split(','))

    # Flash workout plan to the user
    flash(workout_plan)

    # Redirect to the main page
    return redirect(url_for('routes.workout_library', user_id=current_user.id))
# Generates a workout plan based on the user's fitness level, goal, and preferred exercises
def generate_workout_plan(fitness_level: str, goal: str, preferred_exercises: List[str]) -> str:
    # Create a dictionary with the user's fitness level, goal, and preferred exercises
    workout_plan = {

        'fitness_level': fitness_level,
        'goal': goal,
        'exercises': preferred_exercises
    }

    # Empty string to store the workout plan, for key and value in workout_plan, add the key and value to a string
    workout_plan_str = ''
    for key, value in workout_plan.items():
        workout_plan_str += f'{key.capitalize()}: {value}<br>'

    return workout_plan_str

@plans.route('/delete_workout_plan', methods=['POST'])
@login_required
def delete_workout_plan() -> Any:
    # Get the form data
    conn = sqlite3.connect('database.db')
    curs = conn.cursor()
    curs.execute('DELETE FROM workout_plans WHERE user_id=?', (current_user.id,))
    conn.commit()
    conn.close()

    # Redirect to the main page
    return redirect(url_for('routes.workout_library', user_id=current_user.id))

