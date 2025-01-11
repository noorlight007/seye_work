from datetime import datetime
from mongoengine import Document, StringField, ListField, DictField, DateTimeField, SequenceField

class Notifications(Document):
    id = SequenceField(primary_key=True)
    user_whatsapp = StringField()  # Example: IM1 MARIA
    user_profile_name = StringField()
    condition = DictField()  # {"name": query, "id": ""}
    seen = StringField(default='no')
    created_at = DateTimeField()
    updated_at = DateTimeField()

def create_notification(user_whatsapp, user_profile_name, condition):
    if not isinstance(condition, dict):
        raise ValueError("Condition must be a dictionary.")

    new_notification = Notifications(
        user_whatsapp=user_whatsapp,
        user_profile_name=user_profile_name,
        condition=condition,  # Initialize the list with the condition
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    new_notification.save()
    return new_notification

def update_notification_seen(notification_id):
    result = Notifications.objects(id=notification_id).update_one(set__seen="yes")

    if result == 0:
        print("No notification found with the given ID.")
    else:
        print("Notification status changed.")

def get_all_notifications():
    notifications = Notifications.objects.order_by('-created_at')
    return notifications


def get_num_of_notifications():
    return Notifications.objects.count()