def get_country_from_code(phone_number):
    code = phone_number[:3]
    country = "outside"
    if code == "+221":
        country = "Sénégal"

    elif code == "+224":
        country = "Guinée Conakry"
    
    elif code == "+225":
        country = "Côte d’Ivoire"

    return country
