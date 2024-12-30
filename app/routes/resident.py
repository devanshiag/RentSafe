from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from app import db, bcrypt
from app.models import Lease, Lessee, Property, Apartment, Payment, MaintenanceRequest, User
from app.forms import ResidentLoginForm, ResidentRegistrationForm, PaymentForm, MaintenanceRequestForm, ResetPasswordForm, RequestResetForm
from app.services.notification_service import get_user_notifications, mark_as_read, get_unread_notification_count, get_recent_notifications
from app.services.email_service import send_email
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime, timedelta, date
from decimal import Decimal

resident = Blueprint('resident', __name__)

@resident.route('/resident/login', methods=['GET', 'POST'])
def resident_login():
    if current_user.is_authenticated:
        return redirect(url_for('resident.resident_dashboard'))
    
    resident_login_form = ResidentLoginForm()
    if request.method == 'POST':  
        if resident_login_form.validate_on_submit():
            user = User.query.filter_by(username = resident_login_form.username.data).first()
            if user and bcrypt.check_password_hash(user.password_hash, resident_login_form.password.data):
                login_user(user, remember=resident_login_form.remember.data)
                return redirect(url_for('resident.resident_dashboard'))
            else:
                current_app.logger.warning(f"Form submission failed. Errors: {resident_login_form.errors}")
                flash(f"Login Unsuccessful. Please check username and password.", "danger") 
        
    return render_template("resident/login.html", form = resident_login_form, current_page = request.endpoint)

@resident.route('/resident/register', methods=['GET', 'POST'])
def register_resident():
    if current_user.is_authenticated:
        return redirect(url_for('resident.resident_dashboard'))
    
    resident_registration_form = ResidentRegistrationForm()
    if request.method == 'POST':  
        if resident_registration_form.validate_on_submit():

            username = resident_registration_form.username.data
            email = resident_registration_form.email.data
            mobile_number = resident_registration_form.registered_mobile.data
            unit_number = resident_registration_form.apartment_number.data
            last_name = resident_registration_form.last_name.data

            lessee = Lessee.query.filter_by(
            mobile_number=mobile_number,
            apartment_id=unit_number,
            last_name=last_name).first()

            if lessee:
                hashed_password = bcrypt.generate_password_hash(resident_registration_form.password.data).decode('utf-8')
            
                # Check if username or email already exists
                # if User.query.filter_by(username=username).first():
                #     flash('Username already taken. Please choose a different one.', 'danger')
                #     return redirect(url_for('register_resident'))

                # if User.query.filter_by(email=email).first():
                #     flash('Email already registered. Please log in.', 'danger')
                #     return redirect(url_for('resident_login'))

                new_user = User(username=username, password_hash = hashed_password, email = email, mobile_number = mobile_number, apartment_id = unit_number, lessee_id = lessee.id, property_id = lessee.property_id)
                db.session.add(new_user)
                db.session.commit()

                current_app.logger.info(f"Account created successfully for {resident_registration_form.username.data}!")

                flash(f"Your account has been created! You are now able to log in", 'success')
                return redirect(url_for('resident.resident_login'))
            else:
                flash('Registration failed. The provided details do not match any registered lessee.', 'danger')
                return redirect(url_for('resident.register_resident'))
        else:
            current_app.logger.warning(f"Form submission failed. Errors: {resident_registration_form.errors}")
    return render_template("resident/register.html", form = resident_registration_form)

def send_reset_email(user):
    token = user.get_reset_token()
#     msg = Message(subject = 'Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
#     msg.body = f'''To reset your password, visit the following link:
# {url_for('resident_reset_token', token = token, _external=True)}

# If you did not make this request then simply ignore this email and no changes will be made.
# '''
#     mail.send(msg)
    subject = 'Password Reset Request'
    sender='noreply@demo.com'
    recipients=[user.email]
    body = f'''To reset your password, visit the following link:
{url_for('resident.resident_reset_token', token = token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    send_email(subject=subject, sender=sender, recipients=recipients, body=body)

@resident.route('/resident/reset_password', methods=['GET', 'POST'])
def resident_reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('resident.resident_dashboard'))

    reset_form = RequestResetForm()
    if reset_form.validate_on_submit():
        user = User.query.filter(User.email == reset_form.email.data).first()
        if user:
            send_reset_email(user)
            flash('An email has been sent with instructions to reset your password.', 'info')
        else:
            flash('No account found with that email address.', 'warning')
        return redirect(url_for('resident.resident_login'))
    
    return render_template('resident/reset_request.html', form=reset_form)


@resident.route('/resident/reset_password/<token>', methods=['GET', 'POST'])
def resident_reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('resident.resident_dashboard'))
    user = User.verify_reset_token(token)
    if not user:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('resident.resident_reset_request'))
    reset_password_form = ResetPasswordForm()
    if reset_password_form.validate_on_submit():
            
            hashed_password = bcrypt.generate_password_hash(reset_password_form.password.data)

            user.password_hash = hashed_password
            db.session.commit()
            flash('Your password has been updated! You are now able to log in', 'success')
            return redirect(url_for('resident.resident_login'))

    return render_template('resident/reset_token.html', form = reset_password_form)
    
@resident.route('/resident/logout')
def resident_logout():
    logout_user()
    return redirect(url_for('main.home'))

@resident.route('/resident/dashboard', methods=['GET', 'POST'])
@login_required
def resident_dashboard():
    return render_template("resident/dashboard.html", user_role = current_user.role, current_page = request.endpoint)

@resident.route('/resident/lease_info', methods=['GET'])
@login_required
def view_lease_info():
    resident_id = current_user.id
    lessee_id = current_user.lessee_id
    current_app.logger.info(f"current user's id is {resident_id}")

    lease = (
        db.session.query(Lease, Apartment, Property)
        .join(Apartment, Lease.apartment_id == Apartment.id)
        .join(Property, Apartment.property_id == Property.id)
        .filter(Lease.lessee_id == lessee_id)
        .first()
    )

    if not lease:
        return "No lease information available.", 404

    lease_info = {
        "apartment_number": lease.Apartment.id,
        "property_name": lease.Property.name,
        "lease_start_date": lease.Lease.start_date.strftime("%B %d, %Y"),
        "lease_end_date": lease.Lease.end_date.strftime("%B %d, %Y"),
        "monthly_rent": lease.Lease.monthly_rent,
        "next_due_date": lease.Lease.next_due_date.strftime("%B %d, %Y"),
        "lease_document_url": lease.Lease.lease_document_url  # File URL
    }

    return render_template("resident/lease_info.html", lease_info=lease_info, user_role = current_user.role, current_page = request.endpoint)

@resident.route('/resident/payment', methods=['GET', 'POST'])
@login_required
def make_payment():
        user = User.query.filter_by(id = current_user.id).first()
        payment_form = PaymentForm()

        if user:
            lessee = Lessee.query.filter_by(id = user.lessee_id).first()
            lease = lessee.lease
        if lease:
            processing_fee = Decimal('0.0')
            total_amount = lease.monthly_rent

            if request.method == 'POST':
                if payment_form.validate_on_submit():
                    payment_method = payment_form.payment_method.data

                    if payment_method == 'Credit/Debit Card':
                        processing_fee = lease.monthly_rent * Decimal('0.028')

                    total_amount = lease.monthly_rent + processing_fee

                    payment = Payment(lease_id=lease.id, rent_amount=lease.monthly_rent, payment_method=payment_method, processing_fee=processing_fee, total_amount=total_amount, status = 'Completed')
                    db.session.add(payment)

                    # Update next_due_date
                    lease.next_due_date += timedelta(days=30)  # Assuming monthly rent
                    db.session.commit()

                    flash(f'Payment of ₹{total_amount:.2f} successful!', 'success')
                    return redirect(url_for('resident.view_lease_info'))
                else:
                    current_app.logger.warning(f"Form submission failed. Errors: {payment_form.errors}")
                
            return render_template('resident/payment.html', form=payment_form, lease=lease, processing_fee = processing_fee, total_amount = total_amount, user_role = current_user.role, current_page = request.endpoint)       

        else:
            return "No lease found for current user"

    
@resident.route('/resident/new_request', methods=['GET', 'POST'])
@login_required
def create_maintenance_request():
    request_form = MaintenanceRequestForm()
    if request_form.validate_on_submit():
        maintenance_request = MaintenanceRequest(
            user_id=current_user.id,
            apartment_id = current_user.apartment_id,
            property_id = current_user.property_id,
            severity=request_form.severity.data,
            category=request_form.category.data,
            description=request_form.description.data
        )
        db.session.add(maintenance_request)
        db.session.commit()

        flash('Your maintenance request has been submitted successfully!', 'success')
        return redirect(url_for('view_open_requests'))  
    return render_template('resident/new_request.html', form=request_form, user_role = current_user.role, current_page = 'requests')


@resident.route('/resident/open_requests', methods=['GET'])
@login_required
def view_open_requests():
    user = User.query.get(current_user.id)
    
    open_requests = MaintenanceRequest.query.filter(
        MaintenanceRequest.user_id == user.id,
        MaintenanceRequest.status.in_(['Open', 'Deferred', 'In Progress'])
    ).all()
    
    return render_template('resident/maintenance_requests.html', requests=open_requests, heading = 'Open Requests', user_role = current_user.role, current_page = 'requests')


@resident.route('/resident/closed-requests')
@login_required
def closed_requests():
    closed_requests = MaintenanceRequest.query.filter_by(status="Closed").all()
    return render_template('resident/maintenance_requests.html', requests=closed_requests, heading = 'Closed Requests', user_role = current_user.role, current_page = 'requests')

@resident.route('/notifications', methods=['GET'])
@login_required
def notifications():
    notifications = get_user_notifications(current_user.id)
    return render_template('resident/notifications.html', notifications=notifications, user_role=current_user.role, current_page = request.endpoint)

@resident.route('/notifications/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_as_read(notification_id):
    if not current_user.is_authenticated:
        return jsonify(success=False), 403

    success = mark_as_read(notification_id, current_user.id)
    if not success:
        return jsonify(success=False), 403
    return jsonify(success=True)

@resident.context_processor
def inject_notifications():
    if current_user.is_authenticated:
        unread_count = get_unread_notification_count(current_user.id)
        recent_notifications = get_recent_notifications(current_user.id)
        return {"unread_count": unread_count, "notifications": recent_notifications}
    return {}
