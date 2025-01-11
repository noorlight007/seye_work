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
    source = StringField()    # whatsapp bot, insta bot, messenger bot
    created_at = DateTimeField()

# create a new quote
def create_new_quote(client_name, client_whatsapp, phone, email, source):
    new_quote = Quotes(
        client_full_name = client_name,
        client_whatsapp = client_whatsapp,
        phone = phone, 
        email = email,
        source = source,
        created_at = datetime.now()
    )
    new_quote.save()
    return new_quote.id


# Update a quote status
def update_quote_status(quote_id):
    quote = Quotes.objects(id = quote_id).first()
    if quote:
        if quote.status == "open":
            quote.status = "closed"
            quote.save()
        else:
            quote.status = "open"
            quote.save()
        return True, quote.status
    else:
        return False, False

def get_all_quotes():
    quotes = Quotes.objects.order_by('-created_at')
    return quotes

def get_num_of_quotes():
    return Quotes.objects.count()