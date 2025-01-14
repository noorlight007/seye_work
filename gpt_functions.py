from openai import OpenAI
from datetime import datetime, timedelta

import os
from dotenv import load_dotenv
load_dotenv()

openAI_key = os.getenv('OPENAI_API')

## Function to upload file into OpenAI
def saveFile_intoOpenAI(file_location):
    client = OpenAI(api_key=openAI_key)
    file = client.files.create(
        file=open(file_location, "rb"),
        purpose='assistants'
    )
    return file.id

# Delete file from openai
def deleteFile(file_id):
    client = OpenAI(api_key=openAI_key)
    file_deletion_status = client.files.delete(file_id = file_id)

    return file_deletion_status


# Creating assistant
def create_assistant(assistant_name, my_instruction):
    client = OpenAI(api_key=openAI_key)
    my_assistant = client.beta.assistants.create(
        name = assistant_name,
        description= "Virtual assistant of Sablux Holding company of a real state development company, your name is Anna. You will act like a sale representative of this builders company, answer to the customers queries and suggest properties like a pro.",
        instructions = my_instruction,
        model="gpt-4-turbo",
        tools=[{"type": "file_search"},
               {
                "type": "function",
                "function": {
                    "name": "check_which_country",
                    "description": "Whenever a customer sends first message in a thread, you will run this function to get the customer's country name",
                    "parameters": {
                        "properties": {
                            "country_find": {
                                "description": "Alawys returns True when executing this function.",
                                "title": "country_find",
                                "type": "boolean"
                            }

                        },
                        "required": [
                            "country_find"
                        ],
                        "type": "object"
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_property_by_name",
                    "description": "Get a whole property info, details and other info by a property name. A customer will ask you about a property with a name. You will confirm the name with another message if this is the property name the customer is looking for. If they confirm, you will execute this function.",
                    "parameters": {
                        "properties": {
                            "property_name": {
                                "description": "The specific property name the customer is looking for",
                                "title": "Property Name",
                                "type": "string"
                            }
                        },
                        "required": [
                            "property_name"
                        ],
                        "type": "object"
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_all_properties",
                    "description": "Get all the properties of our builders company. You will store all the properties data which will be returned to you, in your memory, no need to show the returned data at once to the customer. So that you can suggest the customer based on their customized choice",
                    "parameters": {
                        "properties": {
                            "return_data": {
                                "description": "You will always return True if this function is executed.",
                                "title": "Return data",
                                "type": "boolean"
                            }
                        },
                        "required": [
                            "return_data"
                        ],
                        "type": "object"
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "contact_admin",
                    "description": "By executing this function, the company admin will be notified about the customer's inquiry.",
                    "parameters": {
                        "properties": {
                            "customer_name": {
                                "description": "The fullname of the customer",
                                "title": "Fullname of Customer",
                                "type": "string"
                            },
                            "phone_number": {
                                "description": "The phone number of the customer",
                                "title": "Phone number of Customer",
                                "type": "string"
                            },
                            "email": {
                                "description": "The email address of the customer",
                                "title": "Email address of Customer",
                                "type": "string"
                            },
                        },
                        "required": [
                            "customer_name",
                            "phone_number",
                            "email"
                        ],
                        "type": "object"
                    }
                }
            }
        ],
	)
    return my_assistant.id

def show_assistants():
    client = OpenAI(api_key=openAI_key)
    my_updated_assistant = client.beta.assistants.list()
    return my_updated_assistant

def updateAssistantInstruction(assistant_id,new_instruction):
    client = OpenAI(api_key=openAI_key)
    my_updated_assistant = client.beta.assistants.update(assistant_id,instructions=new_instruction)
    return my_updated_assistant

def updateAssistantVectorDB(assistant_id, vector_store_id):
    client = OpenAI(api_key=openAI_key)
    assistant = client.beta.assistants.update(
        assistant_id=assistant_id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
    )


# Create a vector store 
def create_vector_store(store_name):
    client = OpenAI(api_key=openAI_key)
    vector_store = client.beta.vector_stores.create(name=store_name)
    return vector_store.id


# upload file into a vector store 
def upload_file_into_vector_store(vector_store_id ,file_ids):
    client = OpenAI(api_key=openAI_key)
 
    file_batch = client.beta.vector_stores.file_batches.create(
        vector_store_id=vector_store_id, file_ids=file_ids
    )
 
    # Print the status and the file counts of the batch to see the result of this operation.
    print(file_batch.status)
    print(file_batch.file_counts)

    print("Done Uploading")
    return file_batch.status


def delete_vector_store_file(vector_store_id, file_id):
    client = OpenAI(api_key=openAI_key)

    deleted_vector_store_file = client.beta.vector_stores.files.delete(
        vector_store_id=vector_store_id,
        file_id=file_id
    )
    print(deleted_vector_store_file)


## Create the Thread
def createThread(prompt):
    client = OpenAI(api_key=openAI_key)
    messages = [{"role":"user", "content": prompt}]
    thread = client.beta.threads.create(messages = messages)
    return thread.id


## Run the Assitance
def runAssistant(thread_id, asssitant_id):
    client = OpenAI(api_key=openAI_key)
    run = client.beta.threads.runs.create(thread_id = thread_id, assistant_id = asssitant_id)
    return run


def sendNewMessage(thread_id,prompt):
    client = OpenAI(api_key=openAI_key)
    thread_message = client.beta.threads.messages.create(thread_id, role= "user", content = prompt)


# Create thread
def initiate_interaction(user_message):
    client = OpenAI(api_key=openAI_key)
    my_thread = client.beta.threads.create(
        messages=[
            {
            "role": "user",
            "content": user_message
            }
        ]
    )
    return my_thread.id


# sending message to existing thread
def sendNewMessage_to_existing_thread(thread_id,message):
    client = OpenAI(api_key=openAI_key)
    thread_message = client.beta.threads.messages.create(thread_id, role= "user", content = message)


# starting a thread
def trigger_assistant(my_thread_id, my_assistant):
    client = OpenAI(api_key=openAI_key)
    run = client.beta.threads.runs.create(thread_id = my_thread_id, assistant_id = my_assistant)
    return run


## See run status
def checkRunStatus(thread_id, run_id):
    client = OpenAI(api_key=openAI_key)
    run = client.beta.threads.runs.retrieve(thread_id = thread_id, run_id = run_id)
    return run

## Retrieve Response from the thread
def retrieveResponse(thread_id):
    client = OpenAI(api_key=openAI_key)
    thread_messages = client.beta.threads.messages.list(thread_id)
    list_messages = thread_messages.data
    assistant_message = list_messages[0]
    message_text = assistant_message.content[0].text.value
    return message_text