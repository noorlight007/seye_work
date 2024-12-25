from mongoengine import *
from datetime import datetime

# Connection url with Mongodb database
connect(host = "mongodb://127.0.0.1:27017/seye?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.7") #This is a local database, that's why the string looks like this.

class Property(Document):
    id = SequenceField(primary_key = True)
    property_name = StringField()  # Example: IM1 MARIA 
    property_type = StringField()  # Example: Land, Villa, Apartment, Office trays
    property_status = StringField()   # Example: Under construction, Launch, Delivered
    property_price = StringField()
    country_place = StringField()  # Example: cote-divoire, guinee-conakry, senegal
    exact_location = StringField()
    description = StringField()
    property_details = DictField()  # Example: {"property_id": ""}
    addess_of_ownership = DictField()  # Example: {"Address": "",,}
    floor_plan = DictField()  # Structure: {"planName": "Appt A","pic_url": "https://...."}
    amenities = ListField(StringField())  # Structure: ["a", "b"]
    property_link = StringField()
    project_type = StringField()  # Example: top_of_the range, economic_villa
    created_at = DateTimeField()
    updated_at = DateTimeField()


def create_new_property(property_name, property_type, property_status, property_price, property_link, project_type):
    check_existing = Property.objects(property_name = property_name).first()
    if check_existing:
        print(f"\nAlready existed property = {property_name}")
    else:
        create_new_record = Property(
            property_name = property_name,
            property_type = property_type,
            property_status = property_status,
            property_price = property_price,
            property_link = property_link,
            project_type = project_type,
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        create_new_record.save()
    
        print(f"\nNew record has updated. Property name: {property_name}")