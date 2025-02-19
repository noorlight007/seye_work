from datetime import datetime, timedelta
import re
import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, session, render_template, jsonify
from flask_session import Session

from twilio.rest import Client
from openai import OpenAI

from gpt_functions import *

from utils import get_country_from_code

from db_manage import *
from db_contacts import *
from db_message_history import *
from db_quotes import *
from db_notifications import *

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
messaging_sid = os.getenv('MESSAGING_SID')
twilio_client = Client(account_sid, auth_token)

ASSISTANT_ID = "asst_Rkvy0lM5kIhPfNe8UnPuHnZx"

from openai import OpenAI
openAI_key = os.getenv('OPENAI_API')

@app.route('/', methods=['GET','POST'])
def index():
    notifications = get_all_notifications()
    num_of_contacts = get_num_of_contacts()
    num_of_messages = get_num_of_messages()
    num_of_quotes = get_num_of_quotes()
    count_items = {"num_of_contacts": num_of_contacts, "num_of_messages": num_of_messages, "num_of_quotes":num_of_quotes}
    return render_template('index.html', notifications = notifications, count_items = count_items)

@app.route('/whatsapp_bot', methods=['GET','POST'])
def whatsapp_bot():
    notifications = get_all_notifications()
    return render_template('whatsapp_dashboard.html', notifications = notifications)

@app.route('/whatsapp_bot/contacts', methods=['GET','POST'])
def contacts():
    notifications = get_all_notifications()
    return render_template('contacts.html', notifications = notifications)


@app.route('/api/contacts', methods=['GET'])
def fetch_contacts():
    contacts = get_all_contacts()
    contacts_data = [
        {
            "profile_name": contact.profile_name,
            "whatsapp": contact.whatsapp,
            "created_at": contact.created_at.strftime('%Y-%m-%d %H:%M:%S') if contact.created_at else '',
        }
        for contact in contacts
    ]
    return jsonify(contacts_data)


@app.route('/quotes-requests', methods=['GET','POST'])
def quotes():
    notifications = get_all_notifications()
    return render_template('quotes.html', notifications = notifications)

@app.route('/api/quotes', methods=['GET'])
def fetch_quotes():
    quotes = get_all_quotes()
    quotes_data = [
        {
            "id": quote.id,
            "client_full_name": quote.client_full_name,
            "client_whatsapp": quote.client_whatsapp,
            "phone":quote.phone,
            "email": quote.email,
            "source": quote.source,
            "status": quote.status,
            "created_at": quote.created_at.strftime('%Y-%m-%d %H:%M:%S') if quote.created_at else '',
        }
        for quote in quotes
    ]
    return jsonify(quotes_data)

@app.route('/api/quotes/update_status/<int:quote_id>', methods=['POST'])
def update_quote_status(quote_id):
    result, new_status= update_quote_status(quote_id)
    
    if result:
        return jsonify({"success": True, "new_status": new_status}), 200
    else:
        return jsonify({"success": False, "message": "Quote not found"}), 404


@app.route('/whatsapp_bot/message_history', methods=['GET','POST'])
def message_history():
    all_contacts = get_all_contacts()
    notifications = get_all_notifications()
    return render_template('message_history.html' , all_contacts = all_contacts, notifications = notifications)

# @app.route('/message_sending', methods=['GET','POST'])
# def message_sending():
#     message_content = ""
#     client_whatsapp = ""
#     # sends twilio whatsapp message to the client



######################    TESTING    ################################

@app.route('/get_messages', methods=['GET','POST'])
def get_messages():
    whatsapp = request.json.get('whatsapp')
    messages, latest_message = get_messages_by_whatsApp(whatsapp)
    
    # Check if the last user message is more than 24 hours old
    can_send_message = True
    if latest_message and latest_message.role == 'user':
        time_diff = datetime.now() - latest_message.created_at
        if time_diff > timedelta(hours=24):
            can_send_message = False
    
    auto_message = check_auto_message_status(whatsapp)

    message_list = [
        {
            "role": msg.role,
            "content": msg.message_content,
            "created_at": msg.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "contact_name": msg.contact_profile_name,
        }
        for msg in messages
    ]
    
    return jsonify({
        "messages": message_list,
        "can_send_message": can_send_message,
        "auto_message": auto_message
    })

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    whatsapp = data.get('whatsapp')
    message_content = data.get('message').strip()
    if message_content.lower() == "exit" or message_content.lower() == "quit":
        update_contact_auto_message(whatsapp, "active")
    update_contact_auto_message(whatsapp, 'stop')
    final_message = f'''~ *Admin* ~
    
{message_content}'''
    twilio_client.messages.create(
        from_= messaging_sid,
        body= final_message,
        to= f"whatsapp:{whatsapp}"
    )
    create_message_history(whatsapp, "bot","bot",message_content.replace('\\n','<br>'))
    # Create new bot message
    
    return jsonify({"success": True})

@app.route('/update_auto_message', methods=['POST'])
def update_auto_message():
    data = request.json
    whatsapp = data.get('whatsapp')
    status = data.get('status')

    if whatsapp and status:
        update_contact_auto_message(whatsapp, status)
        return jsonify({"success": True, "message": "Auto message status updated successfully."})
    else:
        return jsonify({"success": False, "message": "Invalid data provided."}), 400




#########################   END     ##############################

@app.route('/whatsapp', methods=['POST'])
def handle_incoming_message():
    message = request.form.get('Body').strip()
    sender = request.form.get('From')
    profile_name = request.form.get('ProfileName')
    media_url = request.form.get('MediaUrl0')
    print(message)

    # Managing the contacts
    client_exist = check_if_contact_exist(sender[9:], profile_name)
    
    # Managing message history
    if message == "":
        message = "media message"
    create_message_history(sender[9:], profile_name, "user", message)


    if media_url:
        message_created = twilio_client.messages.create(
            from_= phone_number,
            body= "Currently I can't read media files. Please continue with text messaging. Thank you!",
            to= sender
        )

        return "okay", 200
    
    if client_exist.auto_message == 'stop':
        return "okay", 200

    openai_client = OpenAI(api_key=openAI_key)

    # Initializing final response
    final_response = None
    # del request.session[unique_id]
    if "client" not in session:
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
                break
            queue_time+= 1
            
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
                    session['country'] = country_info

                    tool_output={
                        "tool_call_id": tool_call.id,
                        "output": json.dumps({"country":country_info}),
                    }

                    tools_outputs.append(tool_output)
                
                if tool_call.function.name == "get_property_by_name":
                    input_property_name = arguments['property_name']
                    property_data = get_property_by_name(input_property_name)
                    print(property_data)
                    if property_data:
                        tool_output={
                            "tool_call_id": tool_call.id,
                            "output": json.dumps({"found":True,"Property Data":property_data}),
                        }
                    else:
                        tool_output={
                            "tool_call_id": tool_call.id,
                            "output": json.dumps({"found":False}),
                        }
                    tools_outputs.append(tool_output)
                
                if tool_call.function.name == "get_all_properties":
                    all_properties_data = get_properties_by_country(session.get("country"))
                    tool_output={
                            "tool_call_id": tool_call.id,
                            "output": json.dumps({"all_properties_data":all_properties_data}),
                        }
                    tools_outputs.append(tool_output)

                if tool_call.function.name == "contact_admin":
                    fullname = arguments['customer_name']
                    cell_number = arguments['phone_number']
                    email = arguments['email']

                    # Creating a new quote in the database
                    quote_id = create_new_quote(fullname, sender[9:], cell_number, email, "WhatsApp chatbot")
                    create_notification(sender[9:], profile_name, {"name": "query", "id": quote_id})

                    # Send Admin notification
                    twilio_client.messages.create(
                        from_= messaging_sid,
                        content_sid= "HX5df8d742b509e3cc10b187191c202a41",
                        content_variables= json.dumps({"1": fullname,
                                                       "2": cell_number,
                                                       "3": email}),
                        to= "whatsapp:+8801301807991"  
                    )
                    
                    tool_output={
                            "tool_call_id": tool_call.id,
                            "output": json.dumps({"inquiry_sent":True}),
                        }
                    tools_outputs.append(tool_output)


            run = openai_client.beta.threads.runs.submit_tool_outputs(
                thread_id=my_thread_id,
                run_id=run.id,
                tool_outputs=tools_outputs
            )

            
        elif run_status.status == "completed":
            # Extract the bot's response
            final_response = retrieveResponse(my_thread_id)
            print(final_response)
            break

        time.sleep(1)

    print(final_response)
    # Remtion references
    final_response = re.sub(r'【\d+:\d+†source】', '', final_response)
    create_message_history(sender[9:], "bot", "bot", final_response)
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