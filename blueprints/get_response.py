# Import necessary modules
# Import necessary modules
import sqlite3, openai, tempfile, tiktoken, time, asyncio, json, pdfkit, os
from celery import Celery # Brokers: RabbitMQ and Redis
from aiohttp import ClientSession
from flask import render_template, request, session, Blueprint, Response
from flask_login import login_required, current_user
from typing import Tuple
from blueprints.prompts import goal_descriptions, system_prompts, general_format_prompt, test_prompt
from blueprints.calculations import calculate_calorific_needs, calculate_bmr, calculate_bmi, calculate_ideal_body_weight, calculate_macronutrient_split, calculate_body_fat_percentage, healthy_weight_calculator, calculate_tdee, calculate_calories_burnt
from blueprints.function_call import calculate_bmi_description, calculate_ideal_body_weight_description, calculate_macronutrient_split_description, calculate_body_fat_percentage_description, healthy_weight_calculator_description, calculate_tdee_description, calculate_calories_burnt_description, calculate_bmr_description, calculate_calorific_needs_description

# Create blueprint called 'get_response' and set its parameters
get_response = Blueprint('get_response', __name__, template_folder='templates', static_folder='static')

# Configure pdfkit for PDF generation
#config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")


# GET USER INFO FUNCTION
def get_user_info() -> Tuple[str, str, int, int, int, str, str, str]:
    conn = sqlite3.connect('database.db')
    curs = conn.cursor()
    curs.execute("SELECT username, gender, age, height, weight, goal, determination_level, activity_level, bmr_type FROM users WHERE id = (?)", [current_user.id])
    user_data = curs.fetchone()
    conn.close()

    return user_data


#Function to get appropriate advice based on users goal, this will influence the initial plan that is generated
def get_appropriate_advice(user_data: Tuple[str, int, int, int, str, str, str]) -> str:
    pass 


# GET GOAL TIMEFRAME FUNCTION
def get_goal_timeframe(determination_level: str) -> str:
    determination_level_timeframes = {
        'casual': 12,
        'determined': 6,
        'very_determined': 3
    }
    return determination_level_timeframes.get(determination_level, "No timeframe set")

# GET SYSTEM MESSAGE FUNCTION
def get_system_message():
    user_data = get_user_info()
    daily_calorific_needs = calculate_calorific_needs()
    detailed_goal = goal_descriptions.get(user_data[5])
    goal_timeframe = get_goal_timeframe(user_data[6])

    system_message = f"""\n
        User information:
            [
                - Name: ({user_data[0]})
                - Gender: ({user_data[1]})
                - Age: ({user_data[2]} years old)
                - Height: ({user_data[3]}) cm
                - Weight: ({user_data[4]}) kg
                - Goal: ({detailed_goal} in {goal_timeframe} months)
                - Determination Level: ({user_data[6]}) 
                - Activity Level: ({user_data[7]})
                - BMR Type: ({user_data[8]})
                - Daily Calorific Needs: ({daily_calorific_needs})
            ]
        You are a helpful assistant, who is empathetic, patient, motivational, and encouraging, with clear and personalized communication skills.
        """
    print(f"System message: {system_message}")
    return system_message


# GET RESPONSE ROUTE
@get_response.route('/get_response', methods=['GET', 'POST'])
@login_required
def response() -> render_template:

    print("FILE: get_response", "FUNC: response\n\n")
    print("====================================\n")
    # Prints the session
    print("Before:", session)
    print("----------------------------------------------------------------\n")
    
    # Gets variables needed for the response
    user_message = request.form.get('user_message')

    print("User message:", user_message)
    
    # Gets user data
    user_data = get_user_info()
    user_id = current_user.id
    daily_calorific_needs = calculate_calorific_needs()
    bmr = calculate_bmr()
    bmi = calculate_bmi()
    ideal_body_weight = calculate_ideal_body_weight()
    macronutrient_split = calculate_macronutrient_split()
    detailed_goal = goal_descriptions.get(user_data[5])
    system_message = get_system_message()

    # Stores the user data in the session
    session["user_data"] = user_data

    
    # A multi-line string containing the initial instruction for the AI
    initial_system_message = f"""
    Your Persona: Dr. Fit - an expert virtual personal trainer, nutritionist, and doctor with a profound understanding of human physiology, nutrition, and fitness. You are empathetic, patient, motivational, and encouraging, with clear and personalized communication skills.

    Task: Create a concise, easy-to-follow bullet-pointed personalized plan for user {user_id} to achieve their goal: {detailed_goal}. The plan should be based on the user's provided data and titled "Achieving your goal".

    Please follow these guidelines:
    - Address the user directly and in the first person.
    - Focus solely on the essential details.
    - Limit the plan to approximately 1000 words.
    - Maintain a clear and easily understandable bullet list format.

    Users information:[{system_message}]
        
    The plan should cover:
    1. The user's daily caloric and macronutrient intake based on their goal. Include food recommendations and meal examples.
    2. A fitness and workout plan.
    3. A sleep plan.
    4. A nutrition plan.
    5. A happiness plan.
    6. Strategies for achieving the user's detailed goal: {detailed_goal}.
    7. A fact from one of the knowledge topics: {system_prompts} to aid their goal.
    8. An estimated time frame for goal achievement.
    9. A motivational quote.
    10. Yours sincerely, Dr. Fit, please just message me if you have any questions!

    Subsequent responses should be no longer than 150 words and provide answers to the user's questions without offering additional plans.

    Format each plan component as: "<h5><b>Component Title</b></h5><i>Component Explanation</i>". Highlight important details in <b>bold tags</b>. Include a link to a relevant website with more information for each point: <b><i>(<a href="URL" class="response_links">Source</a>)</i></b>.

    The response should start as follows:

    <h3>Hello {user_data[0]}, here's your personalized plan to achieve your goal!</h3>
    <hr>
    <b>Gender</b>: <i>{user_data[1]}</i>
    <b>Age</b>: <i>{user_data[2]} years old</i>
    <b>Height</b>: <i>{user_data[3]} cm</i>
    <b>Weight</b>: <i>{user_data[4]} kg</i>
    <b>Goal</b>: <i>{detailed_goal}</i>
    <b>Activity level</b>: <i>{user_data[7]}</i>
    <b>Determination level</b>: <i>{user_data[6]}</i>
    <b>Daily Calorific Needs</b>: <i>{daily_calorific_needs} calories</i>
    <b>BMR</b>: <i>{bmr} calories</i>
    <b>BMI</b>: <i>{bmi}</i>
    <b>Ideal Body Weight</b>: <i>{ideal_body_weight} kg</i>
    <b>Macronutrient Split</b>: <i>{macronutrient_split}</i>
    <hr>

    Remember do not make your own daily calorific need changes as they have been calculated for the specific user prior 

    """

    enc = tiktoken.get_encoding("cl100k_base")
    print(f"TOKEN COUNT FOR initial_system_message: {len(enc.encode(initial_system_message))}") 

    # A multi-line string containing the determination level instruction for the AI
    determination_level_prompt = f"""
        Task: Determine user's determination level, and provide a response that is appropriate for their determination level.

        For example, if users goal is to get a six pack)


        User Details = {system_message}
        User Goal = ({detailed_goal}

        Determination Levels:
        1. Casual - user is not very determined to achieve their goal
        2. Determined - user is determined to achieve their goal
        3. Very Determined - user is very determined to achieve their goal

        """

    # A multi-line string containing the workout generation instruction for the AI
    workout_generation_prompt = f"""
        Task: Generate a workout plan for user ({user_id}) to achieve their goal: {detailed_goal}. Keep it around 500 words, bullet-pointed, and clear.

        User Details = {system_message}
        User Goal = ({detailed_goal}. For example, if users goal is to achieve a six pack, then encourage them to do more ab workouts)


    """  

    # A multi-line string containing the general instruction for the AI
    general_prompt = f"""
    
        Task: Respond to the user's specific queries based on knowledge from the fields of medicine, personal training, and nutrition.

        User Determination Level: {user_data[6]}
        User Activity Level: {user_data[7]}

        The user's determination and activity levels should inform your advice. For instance, if the user is very determined, your advice should be more rigorous and less flexible.

        User Details(use these details when calculating the function_calls): {system_message}
        Knowledge Topics: {system_prompts}

        Avoid:
        - Asking the user to perform calculations.
        - Using third-person narrative.
        - Advising against the user's goals.
        - Proposing generalized plans or programs.

        Focus on:
        - Providing tailored responses to the user's specific health and fitness questions.
        - Calling the correct functions and outputing there calculations to the user.
        - Using the user's details to provide personalized advice.
        - Formatting your responses in a clear and concise manner, with <b>Bold tags</b> for important details.

        Examples:
        If the user asks: "What should I eat today?"
        You might reply: "Given your goals and current situation, I recommend these foods:"
        Then provide a succinct list.

        For instance:
        [
        User: "What should I eat today?"
        Reply: "In light of your goals and conditions, I suggest these foods:"
        Followed by a brief meal plan.
        ]

        Maintain an informal tone in responses, no need for formal sign-offs.

        Highlight important points and words directly related to the user's health or fitness goals by using <b>bold tags</b>.

        Adapt your responses to the user's specific circumstances while maintaining consistent formatting.

        FUNCTION CALLS:
        - Look for where you could use the functions giving to you, and provide the user with a calculated response.
        - DON'T GIVE THE EXACT VARIABLES TO THE FUNCTIONS (e.g if the user says they're running, don't be exact with the word "running", but anything that is similar to running, like "jogging" or "zipping" is fine)
        - Look at function description to know what the calculation is doing

    """


    # RESPONSE GENERATION
    use_api = True
    #use_api = False

    #Variable initialization for function calling
    model="gpt-4-turbo"
    function_dict = {
    'calculate_bmr': calculate_bmr,
    'calculate_calorific_needs': calculate_calorific_needs, 
    'calculate_bmi': calculate_bmi,
    'calculate_ideal_body_weight': calculate_ideal_body_weight,
    'healthy_weight_calculator': healthy_weight_calculator,
    'calculate_tdee': calculate_tdee,
    'calculate_macronutrient_split': calculate_macronutrient_split,
    'calculate_body_fat_percentage': calculate_body_fat_percentage,
    'calculate_calories_burnt': calculate_calories_burnt
    }
    # List of function descriptions
    functions = [
        calculate_bmr_description,
        calculate_calorific_needs_description,
        calculate_bmi_description,
        calculate_ideal_body_weight_description,
        healthy_weight_calculator_description,
        calculate_tdee_description,
        calculate_macronutrient_split_description,
        calculate_body_fat_percentage_description,
        calculate_calories_burnt_description
    ]
        


    # If there is no use message in main.py, and the press the button, then create the initial plan
    if not user_message:
        print("Create the initial plan if it doesn't exist\n")
        print("current_user.id", current_user.id)
        conn = sqlite3.connect('database.db')
        curs = conn.cursor()
        curs.execute("SELECT initial_plan FROM users WHERE id = ?", (current_user.id,))
        initial_plan = curs.fetchone()
        conn.commit()
        conn.close()

        #INITIAL PLAN GENERATION
        if initial_plan[0]: # If initial plan is not empty
            print("Initial plan already exists:", initial_plan)
        elif not initial_plan[0] and not user_message: # If initial plan is empty and user doesn't send a message, create initial plan
            print("Creating initial plan\n------------------------------------------------------\n")
            if use_api:

                # Calculate the time taken to generate the response
                start_time_initial = time.time()

                res = openai.ChatCompletion.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": initial_system_message},
                    ]
                )
                response = res["choices"][0]["message"]["content"]
                print(response)
                plan = response.replace('\n', '<br>')


                print(f"TIME TAKEN TO GENERATE INITIAL RESPONSE: {time.time() - start_time_initial} seconds")
                enc = tiktoken.get_encoding("cl100k_base")
                print(f"TOKEN COUNT FOR INITIAL RESPONSE: {len(enc.encode(plan))}")
                initial_total_plan_tokens = len(enc.encode(plan)) + len(enc.encode(initial_system_message))
                print(f"INITIAL TOTAL TOKEN COUNT: {initial_total_plan_tokens}")
                print(f"TOKENS LEFT: {4096-initial_total_plan_tokens}\n")
                print("------------------------------------------------------\n")
                

            else: # If not using API, generate simple response
                response = "initial plan... " * 30

            # Update initial_plan in the database
            conn = sqlite3.connect('database.db')
            curs = conn.cursor()
            curs.execute("UPDATE users SET initial_plan = ? WHERE id = ?", (plan, current_user.id))
            conn.commit()
            conn.close()
    
            
    # GENERAL RESPONSE
    elif user_message:
        enc = tiktoken.get_encoding("cl100k_base")
        print(f"TOKEN COUNT FOR GENERAL PROMPT: {len(enc.encode(general_prompt))}\n")

        
        
        start_time_general = time.time() # Starting time for general response 
        if use_api:
            print("USING API")
            print("################", session["conversation"])
            #1st response handling anything
            res1 = openai.ChatCompletion.create(
            model=model,
            messages=[
                        {"role": "system", "content": general_prompt},
                        {"role": "system", "content": general_format_prompt},
                        *session["conversation"],
                        {"role": "user", "content": user_message}
                    ],
            functions=functions # Function call functions that can be used
        )
            
            response_message = res1['choices'][0]['message']
            print(f"Response message 1: {response_message}")
            #session['conversation'].append(response_message) # APPENDING FUNCTION TO AI'S KNOWLEDGE ???

            # Append user message first, regardless of whether a function call occurs or not
            session['conversation'].append({"role": "user", "content": user_message})
            
            #FUNCTION CALL HANDLING
            if 'function_call' in response_message: # If there is a 'function call' in the response

                print("FUNCTION CALL DETECTED")


                # Unpacking function call
                function_name = response_message['function_call']['name'] # Get the name of the function to call
                function_to_call = function_dict[function_name] # Get the function to call
                print("=======================", response_message['function_call']['arguments'])
                function_arguments = json.loads(response_message['function_call']['arguments']) # Get the arguments for the function to call

                print(f"Function name: {function_name}\nFunction to call: {function_to_call}\nFunction arguments: {function_arguments}\n")

                function_response = function_to_call(**function_arguments) #Unpack the arguments and call the function
                #session['conversation'].append({"role": "function", "name": function_name, "content": function_response}) # ALFIE: This is needed for the ai to know why it got the calculation, moved it into the second res generation
                res_2 = openai.ChatCompletion.create(
                    model=model,
                    messages=[
                            {"role": "system", "content": general_prompt},
                            {"role": "system", "content": general_format_prompt},
                            *session["conversation"],
                            {"role": "function", "name": function_name, "content": function_response},
                            {"role": "user", "content": f"The result of the calculation is {function_response}. How should I interpret this?"}
                            ],
                )
                response = res_2['choices'][0]['message']['content']
                print(f"RESPONSE MESSAGE 2: {response}")
                if response == None:
                    response = "Error: No response was generated. Please try again."
                session['conversation'].append({"role": "assistant", "content": response}) # RESPONSE RENDER

            else:
                print('RESPONSE MESSAGE ELSE: ', response_message, '\n')


            enc = tiktoken.get_encoding("cl100k_base")
            if res1:
                # print(f"TOKEN COUNT FOR GENERAL RESPONSE: {len(enc.encode(response))}")
                # print(f"GENERAL TOTAL TOKEN COUNT: {len(enc.encode(str(response))) + len(enc.encode(str(general_prompt))) + len(enc.encode(str(general_format_prompt))) + len(enc.encode(str(user_message)))}\n")
                print("RES1: ", res1)

        # If the API is not used, generate a 'response' to the user message
        else:
            response = "response to: " + user_message
        
        print("ENTERED STUFF OUTSIDE OF FUNCTION")
        #session["conversation"].append({"role": "user", "content": user_message}) # This appends user_message after the response, so I needed to comment it out
        print(f"Response message: {response_message}\n")
        response = response_message['content']
        if response:
            session["conversation"].append({"role": "assistant", "content": response})

        conn = sqlite3.connect('database.db')
        curs = conn.cursor()
        curs.execute("INSERT INTO conversations (user_id, conversation) VALUES (?, ?)",
                     (current_user.id, str({"user": user_message, "assistant": response_message['content']}))) 
                     #(current_user.id, str(session["conversation"])))
        conn.commit()
        conn.close()

        print(f"Time taken to generate general response: {time.time() - start_time_general} seconds\n")
    else:
        response = "No response generated"
        print("Error: No response generated\n")

    

    # Render the main.html template and pass the conversation, user goal and user name to it
    return render_template('main.html', conversation=session["conversation"], 
                           user_goal=current_user.goal)


# Flask route for main page, showing conversation for a specific user
@get_response.route('/main/<int:user_id>')
@login_required
def mainPage(user_id) -> render_template:

    print("ROUTE: main", "FUNC: mainPage\n")
    print("SESSION: ", session)

    # MJN: If no conversation in session then load it from the database
    if not session.get("conversation"):

        print("No conversation in session - loading from the database\n")
        session["conversation"] = []
        conn = sqlite3.connect('database.db')
        curs = conn.cursor()
        curs.execute("SELECT conversation FROM conversations WHERE user_id = (?)", [user_id])
        for row in curs:
            print('xxx',row[0])
            conv_rec = eval(row[0])
            session["conversation"].append({"role": "user", "content": conv_rec['user']})
            response = conv_rec['assistant']
            if response:
                session["conversation"].append({"role": "assistant", "content": response})
        conn.close()
        print(session)

    if not session.get("conversation"):
        session["conversation"] = []

    print("SESSION: ", session)

    return render_template('main.html', conversation=session["conversation"], user_id=user_id, user_goal=current_user.goal)



# GET REPORT ROUTE
@get_response.route('/get_report')
@login_required
def report() -> render_template:

    conn = sqlite3.connect('database.db')
    curs = conn.cursor()
    curs.execute("SELECT initial_plan FROM users WHERE id = ?", (current_user.id,))
    initial_plan = curs.fetchone()
    conn.close()

    print("Setting plan from database", initial_plan[0])
    plan = initial_plan[0] if initial_plan else print("No plan available.\n")

    return render_template('report.html', 
                           user_goal=current_user.goal, 
                           user_name=current_user.username, 
                           generated_report=plan)
    
#DOWNLOAD REPORT ROUTE
@get_response.route('/download_report')
@login_required
def download_report():
    # Fetch the initial plan from the database
    conn = sqlite3.connect('database.db')
    curs = conn.cursor()
    curs.execute("SELECT initial_plan FROM users WHERE id = ?", (current_user.id,))
    initial_plan = curs.fetchone()
    conn.close()
    
    # Check if initial_plan exists
    if initial_plan:
        plan = initial_plan[0]
    else:
        print("No plan available.")
        return "No plan available to download", 404  # Or another appropriate response

    temp_file_path = None # Initialize temporary file path
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp:
        pdfkit.from_string(plan, temp.name)  # Convert plan to PDF
        temp_file_path = temp.name

    # Read the generated PDF and prepare the response
    with open(temp_file_path, 'rb') as temp_file:
        body = temp_file.read()
    
    # Clean up by deleting the temporary PDF file
    os.remove(temp_file_path)
    
    # Return the PDF as a response
    report = Response(body, mimetype='application/pdf')
    report.headers.set('Content-Disposition', 'attachment', filename='report.pdf')
    return report


#INITIAL_PLAN ROUTE
@get_response.route('/get_initial_plan', methods=['GET', 'POST'])
@login_required
def initial_plan() -> render_template:
    conn = sqlite3.connect('database.db')
    curs = conn.cursor()
    curs.execute("SELECT initial_plan FROM users WHERE id = ?", (current_user.id,))
    initial_plan = curs.fetchone()[0]
    conn.close()

    if initial_plan == "":
        response()
        conn = sqlite3.connect('database.db')
        curs = conn.cursor()
        curs.execute("SELECT initial_plan FROM users WHERE id = ?", (current_user.id,))
        initial_plan = curs.fetchone()[0]
        conn.close()

    return render_template('report.html', 
                           user_goal=current_user.goal, 
                           user_name=current_user.username, 
                           generated_report=initial_plan)





