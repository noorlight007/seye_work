from mongoengine import *
from datetime import datetime

# Connection url with Mongodb database
connect(host = "mongodb://127.0.0.1:27017/seye?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.7") #This is a local database, that's why the string looks like this.

class Contacts(Document):
    id = SequenceField(primary_key = True)
    profile_name = StringField()  # Example: IM1 MARIA 
    whatsapp = StringField()
    auto_message = StringField(default = 'active')
    created_at = DateTimeField()
    updated_at = DateTimeField()


# Create a new contact
def create_new_contact(profile_name, whatsapp):
    new_contact = Contacts(
        profile_name = profile_name,
        whatsapp = whatsapp,
        created_at = datetime.now(),
        updated_at = datetime.now()
    )
    new_contact.save()

# If contact is exist
def check_if_contact_exist(whatsapp):
    if_exist = Contacts.objects(whatsapp = whatsapp)
    if if_exist:
        return if_exist
    else:
        return None
    

def get_all_contacts():
    contacts = Contacts.objects.order_by('-created_at')
    return contacts

def check_auto_message_status(whatsapp):
    contact = Contacts.objects(whatsapp = whatsapp).first()
    if contact:
        return contact.auto_message
    else:
        return None

def update_contact_auto_message(whatsapp, status):
    contact = Contacts.objects(whatsapp = whatsapp).first()
    if contact:
        contact.auto_message = status
        contact.save()

