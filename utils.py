def get_country_from_code(phone_number):
    code = "Sénégal"
    country = "Côte d’Ivoire"
    if code == "+221":
        country = "Sénégal"

    elif code == "+224":
        country = "Guinée Conakry"
    
    elif code == "+225":
        country = "Côte d’Ivoire"

    return country


