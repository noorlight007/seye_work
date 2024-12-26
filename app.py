from datetime import datetime, timedelta
import re
import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, session, render_template
from flask_session import Session

from twilio.rest import Client
from openai import OpenAI

from gpt_functions import *

from utils import get_country_from_code

# from link_training import save_to_docx
import json, time

app = Flask(__name__)
app.config['secret_key'] = '5800d5d9e4405020d527f0587538abbe'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

openAI_key = os.getenv('OPENAI_API')
account_sid = os.getenv('ACCOUNT_SID')
auth_token = os.getenv('AUTH_TOKEN')
phone_number = os.getenv('PHONE_NUMBER')
twilio_client = Client(account_sid, auth_token)

ASSISTANT_ID = "asst_zFx2EBwqfNFVhzLMgGQGrRZI"



@app.route('/whatsapp', methods=['POST'])
def handle_incoming_message():
    message = request.form.get('Body')
    sender = request.form.get('From')
    profile_name = request.form.get('ProfileName')
    media_url = request.form.get('MediaUrl0')

    from openai import OpenAI
    openAI_key = os.getenv('OPENAI_API')
    openai_client = OpenAI(api_key=openAI_key)

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
        # Initializing final response
    final_response = None
    # del request.session[unique_id]
    if "openai_" not in session:
        my_thread_id = initiate_interaction(message)
        session["client"] = my_thread_id
    else:
        my_thread_id = session.get("client")
        sendNewMessage_to_existing_thread(my_thread_id, message)

    run = trigger_assistant(my_thread_id, ASSISTANT_ID)
    
    while True:
        run_status = checkRunStatus(my_thread_id , run.id)
        print(f"Run status: {run_status.status}")
        queue_time = 1
        if run_status.status == "failed":
            final_response = "Sorry I am having issues generating responses for queries now. Please wait for me to fix it."
            break
        elif run_status.status == "queued":
            if queue_time == 15:
                session.clear()
                final_response = "Sorry I am having issues generating responses for queries now. Please wait for me to fix it."
                queue_time+= 1
                break
            
        elif run_status.status == "requires_action":
            print("hello")
            # List to store all the call ids
            tools_outputs = []
            print(run_status.required_action.submit_tool_outputs)
            for tool_call in run_status.required_action.submit_tool_outputs.tool_calls:  # Getting all the tool calls
                # The returned parameter value of gpt functions
                arguments = json.loads(tool_call.function.arguments)
                print(f"Function: {tool_call.function.name}\nArgument variables: {arguments}")

                arguments = json.loads(tool_call.function.arguments)

                if tool_call.function.name == "check_which_country":
                    country_info = get_country_from_code(sender[9:])
                    print(country_info)

                    tool_output={
                        "tool_call_id": tool_call.id,
                        "output": json.dumps({"country":country_info}),
                    }

                    tools_outputs.append(tool_output)

            run = openai_client.beta.threads.runs.submit_tool_outputs(
                thread_id=my_thread_id,
                run_id=run.id,
                tool_outputs=tools_outputs
            )

            
        elif run_status.status == "completed":
            # Extract the bot's response
            final_response = retrieveResponse(thread_id)
            print(final_response)
            break

        time.sleep(1)

    print(final_response)
    # Remtion references
    final_response = re.sub(r'【\d+:\d+†source】', '', final_response)
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