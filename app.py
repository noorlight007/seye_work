from datetime import datetime, timedelta

import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, session, render_template
from flask_session import Session

from twilio.rest import Client

from gpt_functions import *

# from link_training import save_to_docx
import json, time

app = Flask(__name__)
app.config['secret_key'] = '5800d5d9e4405020d527f0587538abbe'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

account_sid = os.getenv('ACCOUNT_SID')
auth_token = os.getenv('AUTH_TOKEN')
phone_number = os.getenv('PHONE_NUMBER')
twilio_client = Client(account_sid, auth_token)

ASSISTANT_ID = "asst_lUGfhLsfL4TvgPQrR1kVZkjh"

from openai import OpenAI
openAI_key = os.getenv('OPENAI_API')
client = OpenAI(api_key=openAI_key)

@app.route('/whatsapp', methods=['POST'])
def handle_incoming_message():
    message = request.form.get('Body')
    sender = request.form.get('From')
    profile_name = request.form.get('ProfileName')
    media_url = request.form.get('MediaUrl0')

    if 'thread_id' not in session:
        thread_id = initiate_interaction(message)
        session['thread_id'] = thread_id
    else:
        thread_id = session.get('thread_id')
        sendNewMessage_to_existing_thread(thread_id, message)

    run = trigger_assistant(thread_id, ASSISTANT_ID)
    final_response = "No message"
    while True:
        run_status = checkRunStatus(thread_id , run.id)
        print(f"Run status: {run_status.status}")
        queue_time = 1
        if run_status.status == "failed":
            final_response = "Sorry I am having issues generating responses for queries now. Please wait for me to fix it."
            session.pop('thread_id', None)
            break
        if run_status.status == "queued":
            if queue_time == 10:
                final_response = "Sorry I am having issues generating responses for queries now. Please wait for me to fix it."
                session.pop('thread_id', None)
                break
            queue_time+= 1
        if run_status.status == "completed":
            # Extract the bot's response
            final_response = retrieveResponse(thread_id)
            break

        time.sleep(0.5)

    print(final_response)
    if len(final_response)>1600:
        partA = final_response[:1400]
        partB = final_response[1400:]
        message_created = twilio_client.messages.create(
            from_= phone_number,
            body= partA,
            to= sender
        )
        
        time.sleep(1)
        message_created = twilio_client.messages.create(
            from_= phone_number,
            body= partB,
            to= sender
        )
        
        
    else:
        message_created = twilio_client.messages.create(
            from_= phone_number,
            body= final_response,
            to= sender
        )

    return "Okay", 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8000)