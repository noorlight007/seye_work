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
    amenities = ListField(StringField())  # Structure: ["a", "b"]
    property_link = StringField()
    project_type = StringField()  # Example: top_of_the range, economic_villa
    created_at = DateTimeField()
    updated_at = DateTimeField()

def create_new_property(property_name, property_type, property_status, property_price, property_link, project_type, country_place, exact_location, description, property_details, amenities):
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
            country_place = country_place,
            exact_location = exact_location,
            description = description,
            property_details = property_details,
            amenities = amenities,
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        create_new_record.save()
    
        print(f"\nNew record has updated. Property name: {property_name}")

# create_record("Kimia residences", "Villa", "En construction", "À partir de 160 Millions FCFA", "https://sabluximmobilier.com/programmes/residences-kimia/", "Résidences secondaires")

def get_property_by_name(property_name):
    property = Property.objects(property_name = property_name).first()
    result = {"Property Name": property.property_name, "Property Type": property.property_type, "Property Status": property.property_status,
              "Property Price": property.property_price, "Property Website link": property.property_link, "Country Place": property.country_place,
              "Property Address": property.exact_location, "Description": property.description, "Detail info":property.property_details,
              "Project Type": property.project_type, "Property Amenities": property.amenities}
    return result

# All properties of a country
def get_properties_by_country(country):
    properties = Property.objects(country_place = country)
    results = []
    for item in properties:
        results.append({"Property Name": item.property_name, "Property Type": item.property_type, "Property Status": item.property_status,
              "Property Price": item.property_price, "Property Website link": item.property_link, "Country Place": item.country_place,
              "Property Address": item.exact_location, "Description": item.description, "Detail info":item.property_details,
              "Project Type": item.project_type, "Property Amenities": item.amenities})
    
    return results
