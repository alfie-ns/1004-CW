# Import necessary libraries
from flask import Blueprint, request, jsonify, render_template
from flask_login import current_user
from blueprints.prompts import goal_descriptions
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
import os, openai, sqlite3

# Load environment variables from .env file
load_dotenv(".env")

# Creates Blueprint for the YouTube functionality
youtube = Blueprint('youtube', __name__)

# Get the user's goal from the database
def get_user_goal():
    # Connect to database
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Get the user's goal
    c.execute("SELECT goal FROM users WHERE id=?", (current_user.id,))
    user_goal = c.fetchone()[0]

    # Close the connection to the database
    conn.close()

    return user_goal


# Function to split into token chunks
def split_into_chunks(text_list, max_chunk_size):
    # Empty lists to store the chunks
    chunks = []
    chunk = []
    chunk_size = 0
    # For each sentence in the transcript
    for text in text_list:
        # If the chunk size is less than or equal the maximum chunk size, appending it to chunk list
        if chunk_size + len(text.split()) <= max_chunk_size:
            chunk.append(text)
            chunk_size += len(text.split()) # Update the chunk size
        else:
            # If the chunk size is greater than the maximum chunk size, append the chunks to the chunks list
            chunks.append(" ".join(chunk))
            chunk = [text]
            chunk_size = len(text.split())
    if chunk:  # For the last chunk
        chunks.append(" ".join(chunk))
    return chunks

def get_interpretation_chunks(chunks):
    model = "gpt-4-turbo"
    responses = [] # Empty list to store the responses
    user_goal = goal_descriptions[get_user_goal()] # Get descriptive goal
    print("USERS GOAL: ", user_goal)

    # Message to instruct the model
    app_system_prompt = f"""
        You are assisting in interpreting a YouTube video. Your task is to generate two distinct lists of 10 insights each from the video:
        1. 10 unique insights beneficial to general health.
        2. 10 unique insights beneficial for the user achieving their goal, which is: {user_goal}.
        Please note:
        - Each list should contain exactly 10 bullet points.
        - Begin each bullet point with a '-' character.
        - Ensure the insights are relevant to the video content.

        Format your output as follows:
        <b>Insights for general health:</b> 
        - Insight 1 
        - Insight 2 
        ...
        - Insight 10
        <b>Insights for achieving your goal({get_user_goal()}):</b> 
        - Insight 1 
        - Insight 2 
        ...
        - Insight 10

        THEN STOP
    """

    # Personal use prompt
    personal_system_prompt = f"""
        You are assisting in interpreting a YouTube video. 
        Your task is to generate a distinct list of all the important insights from the video.
        Please note:
        - The list should contain at least 10 bullet points.
        - Begin each bullet point with a '-' character.
        - Ensure the insights are relevant to the video content.
        """
 

    
    # For each chunk in the chunks list, enumerate over with index
    for i, chunk in enumerate(chunks):
        print(f"LENGTH OF CHUNK {i+1}: {len(chunk.split())}")  # print the number of words in the chunk
        res = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": app_system_prompt},
                {"role": "system", "content": f"You are now interpreting chunk {i+1} out of {len(chunks)}. The next message contains the chunk content."},
                {"role": "user", "content": chunk}
            ]
        )
        response = res['choices'][0]['message']['content'].replace('\n', '<br><br>')
        responses.append(response)

    return responses


# Define a route to render the get_youtube.html page when a GET request is made to '/get_youtube'
@youtube.route('/get_youtube', methods=['GET'])
def get_youtube():
    return render_template('get_youtube.html')

# Define a route to handle POST requests to '/captions', where the captions for a YouTube video are retrieved
@youtube.route('/captions', methods=['POST'])
def get_captions():
    # Retrieve the video ID from the request data
    video_id = request.json.get('video_id')
    print("/CAPTIONS VIDEO ID: ", video_id)
    # Set up variables for initializing the YouTube API service object
    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = os.getenv("YOUTUBE_API_KEY")

    # Initialize the YouTube API service
    youtube = build(api_service_name, api_version, developerKey=DEVELOPER_KEY)

    # Make a request to the captions.list method of the YouTube API
    caption_request = youtube.captions().list(
        part="snippet", # Part signifies the different properties that we want to retrieve about the caption
        videoId=video_id # Youtube videoId = video_id from request data
    )

    # Execute the request and get the response
    response = caption_request.execute()

    # Extract the IDs of all English captions from the response
    english_captions = [item['id'] for item in response['items'] if item['snippet']['language'] == 'en-US']

    # Return the English caption IDs as a JSON response
    return jsonify({'english_caption_ids': english_captions})

# Define a route to handle POST requests to '/download_captions', where the captions for a YouTube video are downloaded
@youtube.route('/download_captions', methods=['POST'])
def download_captions():
    video_id = request.json.get('video_id')
    print("/DOWNLOAD_CAPTIONS VIDEO ID: ", video_id)

    # Get the transcript for the video
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    print("/DOWNLOAD_CAPTIONS TRANSCRIPT: ", transcript)

    # Extract the sentences from the transcript
    sentences = [entry['text'] for entry in transcript]

    # Split the sentences into chunks of approximately 10000 tokens each
    chunks = split_into_chunks(sentences, 10000)
    print("/DOWNLOAD_CAPTIONS CHUNKS: ", chunks)


    chunked_responses = get_interpretation_chunks(chunks)
    print("/DOWNLOAD_CAPTIONS CHUNKED RESPONSES: ", chunked_responses)

    return jsonify({'responses': chunked_responses})


# Define a route to handle POST requests to '/search', where YouTube videos are searched
@youtube.route('/search', methods=['POST'])
def search_youtube():
    # Retrieve the video ID from the request data
    video_id = request.json.get('video_id')
    print("/SEARCH VIDEO ID: ", video_id)
    # Set up variables for initializing the YouTube API service object
    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = os.getenv("YOUTUBE_API_KEY")

    # Initialize the YouTube API service
    youtube = build(api_service_name, api_version, developerKey=DEVELOPER_KEY)

    # Make a request to the search.list method of the YouTube API
    search_request = youtube.search().list(
        part="snippet",
        q=video_id,
    )

    # Execute the request and get the response
    response = search_request.execute()

    # Extract the video IDs and titles from the response
    video_ids = [{"id": item['id']['videoId'], "title": item['snippet']['title']} for item in response['items'] if item['id']['kind'] == "youtube#video"]

    # Return the video IDs and titles as a JSON response
    return jsonify(video_ids)

