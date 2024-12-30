from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from app import db
from app.models import Lease, Lessee, Apartment, Payment, MaintenanceRequest, User
from app.forms import AdminLoginForm
from flask_login import login_user, current_user, logout_user
from datetime import date
from sqlalchemy import func, literal

admin = Blueprint('admin', __name__)


@admin.route('/admin/rent-report', methods=['GET'])
def rent_report():
    if not current_user.is_authenticated:
        flash("You are logged out. Log in to access.", 'info')
        return redirect(url_for('admin.admin_login'))
    if current_user.role != 'Admin':
        flash("Access Denied: You do not have permission to view this page.", "danger")
        return redirect(url_for('admin.admin_login'))

    today = date.today()

    # Fetch data from the database
    report = (
    db.session.query(
        Apartment.id.label("apartment_id"),
        func.concat(Lessee.first_name, literal(" "), Lessee.last_name).label("resident_name"),
        Lease.monthly_rent,
        func.sum(Payment.rent_amount).label("total_payment_received"),
        Lease.start_date,
        Lease.next_due_date
    )
    .join(Apartment, Lease.apartment_id == Apartment.id)
    .join(Lessee, Lessee.id == Lease.lessee_id)  # Join Lessee to access first_name and last_name
    .join(Payment, Payment.lease_id == Lease.id, isouter=True)  # Include leases with no payments
    .filter(Apartment.property_id == current_user.property_id)  # Admin's property filter
    .group_by(Apartment.id, Lessee.first_name, Lessee.last_name, Lease.monthly_rent, Lease.start_date, Lease.next_due_date)
    .all()
)

    # Enrich data for the report
    enriched_report = []
    for entry in report:
        # Calculate months passed since the lease start date
        days_since_start = (today - entry.start_date).days
        months_passed = max(0, days_since_start // 30)  # Number of 30-day intervals

        # Calculate expected amount
        expected_amount = months_passed * float(entry.monthly_rent)

        # Get total payments received (if no payments, default to 0.0)
        total_payment = float(entry.total_payment_received) if entry.total_payment_received else 0.0

        # Calculate balance
        balance = expected_amount - total_payment

        # adminend data for this lease
        enriched_report.append({
            "apartment_id": entry.apartment_id,
            "resident_name": entry.resident_name,
            "monthly_rent": float(entry.monthly_rent),
            "amount_to_be_paid_till_date": round(expected_amount, 2),
            "total_payment_received": round(total_payment, 2),
            "balance": round(balance, 2),
            "next_due_date": entry.next_due_date.strftime('%B %d, %Y') if entry.next_due_date else "N/A"
        })

    # Render the rent report template
    return render_template('admin/rent_report.html', report=enriched_report, user_role = current_user.role, current_page = request.endpoint)

@admin.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    admin_login_form = AdminLoginForm()
    if admin_login_form.validate_on_submit():
        user = User.query.filter_by(username = admin_login_form.username.data).first()

        if user and user.password_hash == admin_login_form.password.data:
            login_user(user)
            return redirect(url_for('admin.admin_dashboard'))
        else:
            current_app.logger.warning(f"Form submission failed. Errors: {admin_login_form.errors}")
            flash(f"Login Unsuccessful. Please check username and password.", "danger") 
        
    return render_template("admin/login.html", form = admin_login_form, current_page = request.endpoint)

@admin.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if not current_user.is_authenticated:
        flash("You are logged out. Log in to access.", 'info')
        return redirect(url_for('admin.admin_login'))
    
    if current_user.role != 'Admin':
        flash("Access Denied: You do not have permission to view this page.", "danger")
        return redirect(url_for('admin.admin_login'))


    return render_template('admin/dashboard.html', user_role = current_user.role, current_page = request.endpoint)


@admin.route('/admin/requests', methods=['GET'])
def admin_requests():
    if not current_user.is_authenticated:
        flash("You are logged out. Log in to access.", 'info')
        return redirect(url_for('admin.admin_login'))

    if current_user.role != 'Admin':
        flash("Access Denied: You do not have permission to view this page.", "danger")
        return redirect(url_for('admin.admin_login'))
    
    # Fetch requests for admin's property
    requests = MaintenanceRequest.query.filter(MaintenanceRequest.status != 'Closed', MaintenanceRequest.property_id == current_user.property_id).all()

    return render_template('admin/admin_requests.html', requests=requests, user_role = current_user.role, current_page = request.endpoint)

@admin.route('/admin/edit_request/<int:request_id>', methods=['GET', 'POST'])
def update_request(request_id):
    
    if current_user.role != 'Admin':
        flash("Access Denied: You do not have permission to view this page.", "danger")
        return redirect(url_for('admin.admin_login'))


    maintenance_request = MaintenanceRequest.query.get_or_404(request_id)

    if request.method == 'POST':
        # Update the status and admin comments
        maintenance_request.status = request.form['status']
        maintenance_request.admin_comments = request.form['admin_comments']
        db.session.commit()
        flash('Request updated successfully.', 'success')
        return redirect(url_for('admin.admin_requests'))  # Replace with your maintenance requests view

    return render_template('admin/update_request.html', request=maintenance_request, user_role = current_user.role)


@admin.route('/admin/logout')
def admin_logout():
    logout_user()
    return redirect(url_for('main.home'))
