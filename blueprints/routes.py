from flask import Blueprint, render_template, request
from flask_login import current_user, login_required

routes = Blueprint('routes', __name__, template_folder='templates', static_folder='static', static_url_path='/routes/static')


# Renders workout plans page
@routes.route('/workout_library/<user_id>')
@login_required
def workout_library(user_id):
    return render_template('workout_library.html', user_id=user_id, user_goal=current_user)

# Renders community page
@routes.route('/community/<user_id>')
@login_required
def community(user_id):
    return render_template('community.html', user_id=user_id, user_goal=current_user)

# Renders article page
@routes.route('/article_tips/<user_id>')
@login_required
def article_tips(user_id):
    return render_template('article_tips.html', user_id=user_id, user_goal=current_user)

# Renders day planner page
@routes.route('/day_planner/<user_id>')
@login_required
def day_planner(user_id):
    return render_template('day_planner.html', user_id=user_id, user_goal=current_user)

# Renders about page
@routes.route('/about')
def about():
    return render_template('about.html')

@routes.route('/account')
def account_route():
    return render_template('account.html')


    