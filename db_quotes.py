from mongoengine import *
from datetime import datetime

# Connection url with Mongodb database
connect(host = "mongodb://127.0.0.1:27017/seye?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.7") #This is a local database, that's why the string looks like this.

class Quotes(Document):
    id = SequenceField(primary_key = True)
    client_full_name = StringField()  
    client_whatsapp = StringField()
    phone = StringField()
    email = StringField()
    status = StringField(default = "open")     # open , closed, unnecessary
    created_at = DateTimeField()

# create a new quote
def create_new_quote(client_name, client_whatsapp, phone, email):
    new_quote = Quotes(
        client_name = client_name,
        client_whatsapp = client_whatsapp,
        phone = phone, 
        email = email,
        created_at = datetime.now()
    )
    new_quote.save()


# Update a quote status
def update_quote_status(client_whatsapp, new_status):
    quote = Quotes.objects(client_whatsapp = client_whatsapp).find()
    if quote:
        quote.status = new_status
        quote.save()
        return True
    else:
        return False
