from app.models import Notification
from app import db

from flask import request

def get_user_notifications(user_id):
    page = request.args.get('page', 1, type=int)
    return Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).paginate(page = page, per_page=5)

def mark_as_read(notification_id, user_id):
    notification = Notification.query.get(notification_id)
    if not notification or notification.user_id != user_id:
        return False
    notification.is_read = True
    db.session.commit()
    return True

def get_unread_notification_count(user_id):
    return Notification.query.filter_by(user_id=user_id, is_read=False).count()

def get_recent_notifications(user_id, limit=2):
    return Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(limit).all()
