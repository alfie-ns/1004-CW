# Calculative functions Calculations Blueprint

# Imports
from flask import Blueprint, request, render_template
import math, json, os, sqlite3
from flask_login import current_user, login_required
from typing import List, Any, Tuple

# Create blueprint
calculations = Blueprint('calculations', __name__, template_folder='templates')




# Getting user data and unpacking it
def get_user_info():
    """Gets user data from the database and returns it as a tuple"""
    conn = sqlite3.connect('database.db')
    curs = conn.cursor()
    curs.execute("SELECT gender, age, height, weight, goal, determination_level, activity_level, bmr_type, body_fat_percentage, waist, neck, hip FROM users WHERE id = (?)", [current_user.id,])
    user_data = curs.fetchone()
    conn.close()
    return user_data


# A dictionary containing activity factors and their corresponding values of which they will be multiplied by the BMR
activity_factors = {
        "sedentary": 1.1,
        "lightly_active": 1.275,
        "moderately_active": 1.35,
        "very_active": 1.525,
        "extra_active": 1.7
    }

def calculate_calories_burnt(weight=None, activity=None, duration=None, distance=None):
    """ 
    Calculates the amount of calories burnt during an activity,
    including activity, duration, and weight to make the calculation.
    
    Katch Mcardio formula for calculating calories burnt, with Heart Rate
    Men: Calories/min = (-55.0969 + 0.6309 x HR + 0.1988 x weight + 0.2017 x age) / 4.184
    Women: Calories/min = (-20.4022 + 0.4472 x HR - 0.1263 x weight + 0.074 x age) / 4.184

    Or find dataset for MET values?

    Want to use speed in calculating calories burnt for running and cycling, but I can't find a formula for it.
    """
    print(f"ENTERED CALCULATE_CALORIES_BURNED FUNCTION")
    user_data = get_user_info()
    weight = user_data[3] if weight is None else weight
    
    
    activity_mets = {
        "Writing, desk work, using computer": 1.5,
        "Walking slowly": 2.0,
        "Walking, 3.0 mph": 3.0,
        "Sweeping or mopping floors, vacuuming carpets": 3.0,
        "Yoga session with asanas and pranayama": 3.3,
        "Tennis doubles": 5.0,
        "Weight lifting (moderate intensity)": 5.0,
        "Sexual activity, aged 22": 5.8,
        "Aerobic dancing, medium effort": 6.0,
        "Bicycling, on flat, 10–12 mph, light effort": 6.0,
        "Sun salutation (Surya Namaskar, vigorous with transition jumps)": 7.4,
        "Basketball game": 8.0,
        "Swimming moderately": 8.0,
        "Swimming hard": 11.0,
        "Rope jumping (66/min)": 9.8,
        "Football": 10.3,
        "Rope jumping (84/min)": 10.5,
        "Rope jumping (100/min)": 11.0,
        # Different names needed for chatgpt to successfully recognise the activity and call the function
        "jogging": 11.2,
        "running": 11.2,
    }


    if activity is not None and duration is not None:
        met = activity_mets.get(activity)
        print(f"ACTIVITY: {activity} MET value: {met}")
        if met is None:
            raise Exception(f"Unknown activity: {activity}")
        
        if activity == "running" or activity == "bicycling":
            print('##########################', distance, duration)
            speed = distance / (duration / 60) # Speed in km/h?
            print(f"SPEED: {speed}km/h\n DISTANCE: {distance}km\n DURATION: {duration} minutes\n MET: {met}")
            #met = 1.2 + (speed * 0.08) # Formula for calculating MET based on speed, doesn't work well
            print(f"MET: {met}")
            # This is the formula for calculating calories burnt rounded to the nearest integer then converted to a string
            calories_burnt = str(round(float(duration) * (float(met) * 3.5 * float(weight)) / 200))
        else:
            calories_burnt = str(round(float(duration) * (float(met) * 3.5 * float(weight)) / 200))


        print(f"Activity: {activity}\n Duration: {duration}\n Calories burnt: {calories_burnt} \n")

        return calories_burnt

def calculate_body_fat_percentage(gender=None, height=None, body_fat_percentage=None,waist=None,neck=None,hip=None) -> float:
    print("ENTERED CALCULATE_BODY_FAT_PERCENTAGE FUNCTION")
    user_data = get_user_info()

    gender = user_data[0]
    height = user_data[2]
    body_fat_percentage = user_data[8]  # body_fat_percentage can be manually set during registration
    waist = user_data[9]
    waist = float(waist) if waist is not None and waist != '' else None
    neck = user_data[10]
    hip = user_data[11]
    
    if body_fat_percentage == '':
        body_fat_percentage = None

    # If body_fat_percentage is manually set during registration, return it directly
    if body_fat_percentage is not None:
        print("Body fat percentage already set during registration")
        print(f"Body fat percentage: {body_fat_percentage} \n")
        return body_fat_percentage

    # If waist, neck, or hip is None, return "No Body Fat Percentage Data"
    elif waist is None or neck is None or hip is None:
        return "No Body Fat Percentage Data"

    # Body fat percentage calculation using the US Navy method
    if gender == 'male':
        if waist - neck <= 0 or height <= 0:
            print("Invalid measurements for body fat calculation.")
            print(f"waist: {waist}, neck: {neck}, height: {height}")
            return None
        body_fat_percentage = 86.010 * math.log10(waist - neck) - 70.041 * math.log10(height) + 36.76
    elif gender == 'female':
        if waist + hip - neck <= 0 or height <= 0:
            print("Invalid measurements for body fat calculation.")
            return None
        body_fat_percentage = 163.205 * math.log10(waist + hip - neck) - 97.684 * math.log10(height) - 78.387
        print(f"Body fat percentage: {round(body_fat_percentage, 2)} \n")
    
    body_fat_percentage = str(round(body_fat_percentage, 2))
    return body_fat_percentage

def calculate_bmr(gender=None,age=None,height=None,weight=None,bmr_type=None,body_fat_percentage=None) -> int:
    print("ENTERED CALCULATE_BMR FUNCTION")
    """Calculates the BMR of the user based on the BMR type and user data"""

    user_data = get_user_info()

    # Unpacking user data
    gender = user_data[0]
    age = user_data[1]
    height = user_data[2]
    weight = user_data[3]
    bmr_type = user_data[7]
    body_fat_percentage = float(user_data[8]) if user_data[8] is not None and user_data[8] != '' else None


    # Calculating BMR
    if bmr_type == "harris_benedict":
        if gender == "male":
            bmr = 66.4730 + (13.7516 * weight) + (5.0033 * height) - (6.7550 * age)
        elif gender == "female":
            bmr = 655.0955 + (9.5634 * weight) + (1.8496 * height) - (4.6756 * age)
        else:
            raise ValueError(f"Unknown gender: {gender}")
    elif bmr_type == "mifflin_st_jeor": # Minimum BMR required for proper body function
        if gender == "male":
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        elif gender == "female":
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        else:
            raise ValueError(f"Unknown gender: {gender}")
    elif bmr_type == "katch_mcardle":
        # Ensures body fat percentage was provided, if not will calculate it now if other values to calculate it are available
        if body_fat_percentage is None:
            body_fat_percentage = calculate_body_fat_percentage()
            print(f"Body fat percentage calculated: {body_fat_percentage}")
            lean_body_mass = weight * (1 - (float(body_fat_percentage) / 100))  # calculate lean body mass
            bmr = 370 + (21.6 * lean_body_mass)
            if body_fat_percentage == None :
                raise Exception("Body fat percentage is required for Katch-McArdle BMR calculation")
        else:
            lean_body_mass = weight * (1 - (float(body_fat_percentage) / 100))  # calculate lean body mass
            bmr = 370 + (21.6 * lean_body_mass)
    else:
        raise ValueError(f"Unknown BMR type: {bmr_type}")
    
    print(f"Users BMR: {bmr}\n")

    # Update the users BMR in the database
    conn = sqlite3.connect('database.db')
    curs = conn.cursor()
    curs.execute("UPDATE users SET bmr = (?) WHERE id = (?)", [bmr, current_user.id])
    conn.commit()
    conn.close()
    
    bmr = str(round(bmr))

    return bmr


# A function that calculates the daily calorific needs of the user
def calculate_calorific_needs(age=None,height=None,weight=None,goal=None,determination_level=None,activity_level=None) -> int:
    """Calculates the daily calorific needs of the user based on the BMR and activity level"""
    bmr = calculate_bmr()
    user_data = get_user_info()

    print(f"ENTERED CALCULATE CALORIFIC NEEDS FUNCTION.")

    # Unpacking user data
    age = user_data[1]
    height = user_data[2]
    weight = user_data[3]
    goal = user_data[4]
    determination_level = user_data[5]
    activity_level = user_data[6]


    # Lowest BMR possible
    lowest_bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
  
    # If activity level is not in the activity factors dictionary, raise a ValueError
    if activity_level not in activity_factors:
        raise ValueError(f"Unknown activity level: {activity_level}")

    # Calculating daily calorific needs due to activity level
    daily_calorific_needs = int(bmr) * activity_factors[activity_level]


    print(f"Users calorific needs before goal factor implementation: {daily_calorific_needs}")
    # if calorific needs is to low, set it to the minimum BMR required for proper body function
    if goal == "lose_weight" or goal == "six_pack":
        print("Entered lose_weight or six_pack goal factor implementation")
        if determination_level == "casual":
            daily_calorific_needs *= 0.80  # 20% deficit
            if daily_calorific_needs < lowest_bmr * activity_factors[activity_level]:
                print("Entered lowest BMR if statement")
                daily_calorific_needs = lowest_bmr * activity_factors[activity_level]
        elif determination_level == "determined":
            daily_calorific_needs *= 0.70  # 30% deficit
            if daily_calorific_needs < lowest_bmr * activity_factors[activity_level]:
                print("Entered lowest BMR if statement")
                daily_calorific_needs = lowest_bmr * activity_factors[activity_level]
        elif determination_level == "very_determined":
            daily_calorific_needs *= 0.60  # 40% deficit
            if daily_calorific_needs < lowest_bmr * activity_factors[activity_level]:
                print("Entered lowest BMR if statement")
                daily_calorific_needs = lowest_bmr * activity_factors[activity_level]
            
    # If users goal == "bulk"
    elif goal == "bulk":
        print("Entered bulk goal factor implementation")
        if determination_level == "casual":
            daily_calorific_needs *= 1.10  # 10% surplus
        elif determination_level == "determined":
            daily_calorific_needs *= 1.20  # 20% surplus
        elif determination_level == "very_determined":
            daily_calorific_needs *= 1.30  # 30% surplus

    # If users goal == "improve_endurance"
    elif goal == "improve_endurance":
        print("Entered improve_endurance goal factor implementation")
        if determination_level == "casual":
            daily_calorific_needs *= 1.05  # 5% surplus
        elif determination_level == "determined":
            daily_calorific_needs *= 1.10  # 10% surplus
        elif determination_level == "very_determined":
            daily_calorific_needs *= 1.15  # 15% surplus

    # If users goal == "improve_flexibility"
    elif goal == "improve_flexibility":
        print("Entered improve_flexibility goal factor implementation")
        # TODO: No major adjustments to calorific intake but should ensure adequate protein for muscle recovery 
        pass
    # If users goal == "stress_reduction"
    elif goal == "stress_reduction":
        print("Entered stress_reduction goal factor implementation")
        # TODO: No major adjustments to calorific intake but should ensure a balanced diet for overall mental health 
        pass
    # If users goal == "healthy_happiness" or "improve_posture" or "improve_sleep"
    elif goal == "healthy_happiness" or goal == "improve_posture" or goal == "improve_sleep":
        print("Entered healthy_happiness, improve_posture or improve_sleep goal factor implementation")
        # TODO: No adjustments needed as these goals focus on lifestyle habits rather than calorific intake
        pass 
    print(f"Users calorific needs after goal factor implementation: {daily_calorific_needs}\n")
    
    # Round the daily calorific needs to the nearest integer
    daily_calorific_needs = str(round(daily_calorific_needs))

    # Return the daily calorific needs
    return daily_calorific_needs


# Calculate tdee function
def calculate_tdee(bmr=None,activity_level=None) -> int:
    bmr = calculate_bmr()
    user_data = get_user_info()

    print("ENTERED CALCULATE TDEE FUNCTION.")

    # Unpacking user data
    activity_level = user_data[6]


    # Look up the activity factor from the dictionary
    activity_factor = activity_factors.get(activity_level)
    print(f"Activity factor: {activity_factor}")
    if activity_factor is None:
        raise ValueError(f"Unknown activity level: {activity_level}")

    tdee = int(bmr) * activity_factor # Multiply BMR by activity level to get TDEE
    tdee = str(round(tdee)) # Round TDEE to the nearest integer
    print(f"Total Daily Energy Expenditure (TDEE): {tdee}\n")

    return tdee


#calculate_bmi function
def calculate_bmi(height=None, weight=None) -> float:
    user_data = get_user_info()
    print("ENTERED CALCULATE_BMI FUNCTION")
    """Gets the users height and weight from the database and calculates the users BMI"""

    # Unpack user data
    height = user_data[2]
    weight = user_data[3]

    height_m = height / 100 # convert height from cm to m
    bmi = weight / (height_m ** 2)
    bmi = str(round(bmi, 2)) # Round BMI to 2 decimal places

    #TODO: Add more bmi categories(look on notes)
    return bmi



#calculate_ideal_body_weight function
def calculate_ideal_body_weight() -> float:
    user_data = get_user_info()
    print("ENTERED CALCULATE_IDEAL_BODY_WEIGHT FUNCTION")

    gender = user_data[0]
    height = user_data[2]

    print(f"User data inside calculate_ideal_body_weight function: {user_data}")

    height_inch = height / 2.54 # convert height from cm to inch
    if gender == 'male':
        ideal_body_weight_kg = round(50 + 2.3 * (height_inch - 60)) 
    elif gender == 'female':
        ideal_body_weight_kg = round(45.5 + 2.3 * (height_inch - 60))
    else:
        raise ValueError(f"Unknown gender: {gender}")
    
    ideal_body_weight_kg_str = f"{ideal_body_weight_kg} kg"
    ideal_body_weight_lbs_str = f"{round(ideal_body_weight_kg * 2.205)} lb" # convert kg to lbs

    print(f"Ideal body weight in kg: {ideal_body_weight_kg_str} and in lbs: {ideal_body_weight_lbs_str}\n")

    return ideal_body_weight_lbs_str, ideal_body_weight_kg_str


# Get TDEE first 
# Calculate macronutrient split function
def calculate_macronutrient_split(goal=None, tdee=None) -> tuple:
    tdee = calculate_tdee()
    user_data = get_user_info()

    print("ENTERED CALCULATE_MACRONUTRIENT_SPLIT FUNCTION")

    # Unpacking user data
    goal = user_data[4]

    # Balanced diet: moderate protein, carb, and fat
    protein_percentage = 0.2
    fat_percentage = 0.3
    carb_percentage = 0.5

    if goal == 'bulk':
        # Higher protein, high carb, moderate fat
        protein_percentage = 0.3
        carb_percentage = 0.5
        fat_percentage = 0.2
    elif goal == 'lose_weight':
        # Higher protein, moderate fat, lower carb
        protein_percentage = 0.4
        fat_percentage = 0.3
        carb_percentage = 0.3
    elif goal == 'healthy_happiness':
        # Balanced diet: moderate protein, carb, and fat
        protein_percentage = 0.2
        fat_percentage = 0.3
        carb_percentage = 0.5
    elif goal == 'improve_posture' or goal == 'improve_flexibility':
        # Balanced diet: moderate protein, carb, and fat
        protein_percentage = 0.2
        fat_percentage = 0.3
        carb_percentage = 0.5
    elif goal == 'stress_reduction':
        # Balanced diet with emphasis on whole foods
        protein_percentage = 0.2
        fat_percentage = 0.3
        carb_percentage = 0.5
    elif goal == 'improve_endurance':
        # Higher carb intake for energy, moderate protein, lower fat
        protein_percentage = 0.2
        carb_percentage = 0.6
        fat_percentage = 0.2
    elif goal == 'six_pack':
        # Higher protein for muscle building and fat loss, lower carb, moderate fat
        protein_percentage = 0.4
        fat_percentage = 0.3
        carb_percentage = 0.3

    protein_calories = protein_percentage * int(tdee)
    fat_calories = fat_percentage * int(tdee)
    carb_calories = carb_percentage * int(tdee)

    protein_grams = f"{round(protein_calories / 4)} protein grams"
    fat_grams = f"{round(fat_calories / 9)} fat grams"
    carb_grams = f"{round(carb_calories / 4)} carb grams"

    macronutrient_split = f"Protein: {protein_grams}, Fat: {fat_grams}, Carb: {carb_grams} \n"

    print(macronutrient_split ,"\n")

    return str(macronutrient_split)



# Calculate healthy weight function
def healthy_weight_calculator(height=None):
    user_data = get_user_info() # get user data from database
    print("ENTERED HEALTHY_WEIGHT_CALCULATOR FUNCTION")
    """Calculates the users healthy weight range based on their height"""
    height = user_data[2]

    height_meters = height / 100  # convert cm to meters
    lower_weight = 18.5 * (height_meters**2) # lower weight range
    upper_weight = 24.9 * (height_meters**2) # upper weight range
    healthy_weight_range = f"Healthy weight range: {round(lower_weight, 2)} to {round(upper_weight, 2)} \n"
    print(healthy_weight_range,"\n")
    return healthy_weight_range


