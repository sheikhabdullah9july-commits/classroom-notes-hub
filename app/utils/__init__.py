# Utils package
from app import db
from app.models import Notification

def create_notification(user_id, message, notification_type='info'):
    """Create a notification for a user"""
    notification = Notification(
        user_id=user_id,
        message=message,
        type=notification_type
    )
    db.session.add(notification)
    db.session.commit()
    return notification
