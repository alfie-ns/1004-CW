from flask import Blueprint 


function_call_descriptions = Blueprint('function_call_descriptions', __name__)


#FUNCTIONS CALL DESCRIPTIONS
calculate_calorific_needs_description = {
    "name": "calculate_calorific_needs",
    "description": "Calculate the daily calorific needs of a user based on their personal information and fitness goals",
    "parameters": {
        "type": "object",
        "properties": {
            "age": {
                "type": "integer",
                "description": "The user's age in years"
            },
            "height": {
                "type": "integer",
                "description": "The user's height in centimeters"
            },
            "weight": {
                "type": "integer",
                "description": "The user's weight in kilograms"
            },
            "goal": {
                "type": "string",
                "enum": ["lose_weight", "six_pack", "bulk", "improve_endurance", "improve_flexibility", "stress_reduction", "healthy_happiness", "improve_posture", "improve_sleep"],
                "description": "The user's fitness goal"
            },
            "determination_level": {
                "type": "string",
                "enum": ["casual", "determined", "very_determined"],
                "description": "The user's level of determination towards their fitness goal"
            },
            "activity_level": {
                "type": "string",
                "description": "The user's level of physical activity"
            }
        },
        "required": ["gender", "age", "height", "weight", "goal", "determination_level", "activity_level", "bmr_type"]
    }
}
calculate_tdee_description = {
    "name": "calculate_tdee",
    "description": "Calculate the Total Daily Energy Expenditure (TDEE) of a user based on their BMR and activity level",
    "parameters": {
        "type": "object",
        "properties": {
            "bmr": {
                "type": "number",
                "description": "The user's Basal Metabolic Rate (BMR)"
            },
            "activity_level": {
                "type": "string",
                "description": "The user's level of physical activity"
            }
        },
        "required": ["bmr", "activity_level"]
    }
}

healthy_weight_calculator_description = {
    "name": "healthy_weight_calculator",
    "description": "Calculates the user's healthy weight range based on their height",
    "parameters": {
        "type": "object",
        "properties": {
            "height": {
                "type": "integer",
                "description": "The user's height in centimeters"
            }
        },
        "required": ["height"]
    }
}


calculate_bmi_description = {
    "name": "calculate_bmi",
    "description": "Calculate the Body Mass Index (BMI) of a user based on their weight and height",
    "parameters": {
        "type": "object",
        "properties": {
            "weight": {
                "type": "integer",
                "description": "The user's weight in kilograms"
            },
            "height": {
                "type": "integer",
                "description": "The user's height in centimeters"
            }
        },
        "required": ["weight", "height"]
    }
}

calculate_ideal_body_weight_description = {
    "name": "calculate_ideal_body_weight",
    "description": "Calculate the ideal body weight of a user based on their height and gender",
    "parameters": {
        "type": "object",
        "properties": {
            "height": {
                "type": "integer",
                "description": "The user's height in centimeters"
            },
            "gender": {
                "type": "string",
                "enum": ["male", "female"],
                "description": "The user's gender"
            }
        },
        "required": ["height", "gender"]
    }
}

calculate_macronutrient_split_description = {
    "name": "calculate_macronutrient_split",
    "description": "Calculate the macronutrient split of a user based on their TDEE and fitness goal",
    "parameters": {
        "type": "object",
        "properties": {
            "tdee": {
                "type": "number",
                "description": "The user's Total Daily Energy Expenditure (TDEE)"
            },
            "goal": {
                "type": "string",
                "enum": ["lose_weight", "six_pack", "bulk", "improve_endurance", "improve_flexibility", "stress_reduction", "healthy_happiness", "improve_posture", "improve_sleep"],
                "description": "The user's fitness goal"
            }
        },
        "required": ["tdee", "goal"]
    }
}

calculate_body_fat_percentage_description = {
    "name": "calculate_body_fat_percentage",
    "description": "Calculate the body fat percentage of a user based on their measurements and gender",
    "parameters": {
        "type": "object",
        "properties": {
            "height": {
                "type": "integer",
                "description": "The user's height in centimeters"
            },
            "waist": {
                "type": "integer",
                "description": "The user's waist circumference in centimeters"
            },
            "neck": {
                "type": "integer",
                "description": "The user's neck circumference in centimeters"
            },
            "hip": {
                "type": "integer",
                "description": "The user's hip circumference in centimeters"
            },
           "gender": {
                "type": "string",
                "enum": ["male", "female"],
                "description": "The user's gender"
            }
        },
        "required": ["height", "waist", "neck", "hip", "gender"]
    }
}
calculate_bmr_description = {
    "name": "calculate_bmr",
    "description": "Calculates the Basal Metabolic Rate (BMR) based on user data",
    "parameters": {
        "type": "object",
        "properties": {
            "gender": {
                "type": "string",
                "enum": ["male", "female"],
                "description": "The user's gender"
            },
            "age": {
                "type": "integer",
                "description": "The user's age in years"
            },
            "height": {
                "type": "integer",
                "description": "The user's height in centimeters"
            },
            "weight": {
                "type": "integer",
                "description": "The user's weight in kilograms"
            },
            "bmr_type": {
                "type": "string",
                "enum": ["harris_benedict", "mifflin_st_jeor", "katch_mcardle"],
                "description": "The type of Basal Metabolic Rate (BMR) formula to use for the calculations"
            },
            "body_fat_percentage": {
                "type": "integer",
                "description": "The user's body fat percentage (required for Katch-McArdle BMR calculation)"
            }
        },
        "required": ["gender", "age", "height", "weight", "bmr_type", "body_fat_percentage"]
    }
}

calculate_calories_burnt_description = {
    "name": "calculate_calories_burnt",
    "description": "This calculates the calories burnt during an activity based on the user's weight, duration and activity type",
    "parameters": {
        "type": "object",
        "properties": {
            "activity": {
                "type": "string",
                "description": "The user's activity"
            },
            "duration": {
                "type": "integer",
                "description": "The duration of the activity in minutes"
            },
            "weight": {
                "type": "integer",
                "description": "The user's weight in kilograms"
            },
            "distance": {
                "type": "integer",
                "description": "The distance travelled in miles or km, convert miles to metres, same for km to metres, (required for running and cycling)"
            }
        },
        "required": ["activity", "duration", "weight"]
    }
}
