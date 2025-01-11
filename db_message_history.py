from mongoengine import *
from datetime import datetime

# Connection url with Mongodb database
connect(host = "mongodb://127.0.0.1:27017/seye?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.7") #This is a local database, that's why the string looks like this.

class Messages(Document):
    id = SequenceField(primary_key = True)
    whatsappp = StringField()
    contact_profile_name = StringField()
    role = StringField()
    message_content = StringField()
    created_at = DateTimeField()


# Create a new message item
def create_message_history(whatsappp, contact_profile_name, role, message_content):
    new_message = Messages(
        whatsappp = whatsappp,
        contact_profile_name = contact_profile_name,
        role = role,
        message_content = message_content,
        created_at = datetime.now()
    )
    new_message.save()



def get_messages_by_whatsApp(whatsapp):
    messages = Messages.objects(whatsappp=whatsapp).order_by('created_at')
    latest_message = Messages.objects(whatsappp=whatsapp).order_by('-created_at').first()
    return messages, latest_message

def get_num_of_messages():
    return Messages.objects.count()
