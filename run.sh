#!/bin/bash

# Setting Flask application environment variables
export FLASK_APP=app
export FLASK_ENV=development

# Starting Flask application with python3
python3 -m flask run
