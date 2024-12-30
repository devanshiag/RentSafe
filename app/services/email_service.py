from flask_mail import Message
from flask import current_app
from app import mail

def send_email(subject, recipients, body, sender = 'agrdevanshi25@gmail.com'):
    try:
        with current_app.app_context():
            msg = Message(subject=subject, sender=sender, recipients=recipients, body=body)
            
            mail.send(msg)
            current_app.logger.info(f"Email sent to {recipients}")
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {e}")
        