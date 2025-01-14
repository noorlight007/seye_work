from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException, TwilioException

# TWILIO_ACCOUNT_SID = 'AC477fbb2103f52a03c0bcdc8580ebebc8'
# TWILIO_AUTH_TOKEN = 'eb31fdf55378f6d14ceacd90bb97a5a4'

# twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
# print(twilio_client.ser)

# # # def create_messaging_service(service_name):
    
# # #     messaging_service = twilio_client.messaging.v1.services.create(
# # #         friendly_name=service_name,
# # #         usecase='notifications'  # Options: 'notifications', 'marketing', 'otp', etc.
# # #     )
# # #     return messaging_service.sid


# # service = twilio_client.messaging.services("MG4c45316c84bc4b5f25d0694926b7285c")
# # print(service.phone_numbers.list(1))
# # print(create_messaging_service("twilio_testing"))

# phone_numbers = twilio_client.incoming_phone_numbers.list()
# #print(phone_numbers.phone_number)
# # Collect sender details
# senders = []
# for number in phone_numbers:
#     senders.append({
#         "sid": number.sid,
#         "phone_number": number.phone_number,
#         "friendly_name": number.friendly_name,
#         "sid": number.sid,
#         "capabilities": number.capabilities,  # e.g., SMS, MMS, voice, WhatsApp
#     })

# print(senders)

def create_messaging_service(whatsapp_uid, account_sid, auth_token, whatsapp_sender):
    try:
        twilio_client = Client(account_sid, auth_token)
        #print(twilio_client.available_phone_numbers.list(limit=20))
        messaging_service = twilio_client.messaging.v1.services.create(
            friendly_name=f"chatbot_{whatsapp_uid[:6]}",
            usecase='marketing'  # Options: 'notifications', 'marketing', 'otp', etc.
        )

        new_messaging_service = twilio_client.messaging.v1.services(messaging_service.sid)
        
        phone_number_sid = get_phone_number_details(account_sid, auth_token, whatsapp_sender)
        # new_messaging_service.phone_numbers.create(phone_number_sid)
        # If can't found phone number sid
        if not phone_number_sid:
            return {"status": "error", "message": "Phone number not found in your Twilio account"}

        # whatsapp webhook
        update_kwargs = {"inbound_request_url": f"https://afrobeutic.com/salons/page_create_salon/{whatsapp_uid}"}
        # Update the messaging service with incoming message webhook
        new_messaging_service.update(**update_kwargs)
        print(twilio_client.messaging.v1.services(messaging_service.sid).fetch().links)

        #print(f"\n***************\nMessaging SID: {messaging_service.sid}\nPhone number sid: {phone_number_sid}\nAssigned phone number sid: {assigned_phone_number.sid}\n***************")

    except TwilioRestException as e:
        print(e)
    except TwilioException as e:
        print(e)
    except ValueError as e:
        print(e)
    except Exception as e:
        print(e)

# Check if phone number is valid
def get_phone_number_details(account_sid, auth_token, phone_number):
    twilio_client = Client(account_sid, auth_token)
    phone_numbers = twilio_client.incoming_phone_numbers.list()
    for number in phone_numbers:
        if phone_number == number.phone_number:
            return number.sid
    return None


create_messaging_service("wurds4v15s4v15sdv15s6rv41r6w5v1", TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, "+17373772458")