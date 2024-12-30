from apscheduler.schedulers.background import BackgroundScheduler
from flask_mail import Message
from app.services.email_service import send_email
from app import create_app

# Initialize the scheduler
scheduler = BackgroundScheduler()

def rent_due_notifications():
    from app import db  
    from flask import current_app
    from app.models import Lease, User, Notification, Lessee
    from datetime import date, timedelta
    import logging

    with create_app().app_context():  
        today = date.today()
        due_date_threshold = today + timedelta(days=5)
        current_app.logger.info(f"Running rent_due_notifications for {due_date_threshold}")

        # residents with rent due in 5 days
        leases = db.session.query(Lease).filter(Lease.next_due_date == due_date_threshold).all()

        current_app.logger.info(f"Found {len(leases)} leases with due dates")


        for lease in leases:
            user = User.query.filter_by(apartment_id=lease.apartment_id).first()
            lessee_id = lease.lessee_id
            lessee = Lessee.query.filter_by(id = lessee_id).first()

            if lessee and user:
                logging.info(f"Sending notification to {user.username}")
                # Email Notification
                email_body = (
                    f"Dear {lessee.first_name} {lessee.last_name},\n\n"
                    f"Your rent of ₹ {lease.monthly_rent} is due on {lease.next_due_date.strftime('%B %d, %Y')}. "
                    "Please ensure payment before the due date to avoid any hassle. \n\n"
                    f"Regards,\nYour Landlord"
                )
                send_email(
                    subject="Rent Due Reminder",
                    recipients=[user.email],
                    body=email_body
                )

                # In-App Notification
                notification = Notification(
                    user_id=user.id,
                    message=f"Your rent of ₹ {lease.monthly_rent} is due on {lease.next_due_date}."
                )
                db.session.add(notification)
        db.session.commit()
        current_app.logger.info("Notifications committed to the database")


if not scheduler.get_job('rent_due_job'):
    scheduler.add_job(rent_due_notifications, 'interval', days = 1, id='rent_due_job', replace_existing=True)
