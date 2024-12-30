from app import db, login_manager
from datetime import datetime, timedelta
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask import current_app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Property(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(256), nullable=False)

    # Relationship: Property -> Apartments
    apartments = db.relationship('Apartment', backref='property', lazy=True)

    def __repr__(self):
        return f"<Property id: {self.id}, name: {self.name}, Address: {self.address}>"

class Apartment(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)

    # Relationship: Apartment -> Lessees
    lessees = db.relationship('Lessee', backref='apartment', lazy=True)

    # Relationship: Apartment -> Lease
    lease = db.relationship('Lease', backref='apartment', uselist=False, lazy=True)

    # Relationship: Apartment -> Maintenance Requests
    maintenance_requests = db.relationship('MaintenanceRequest', backref='apartment', lazy=True)

    def __repr__(self):
        return f"<Apartment Number: {self.id}, Property ID: {self.property_id}>"

class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    mobile_number = db.Column(db.String(15), nullable=False)
    role = db.Column(db.Enum('Resident', 'Admin', name='user_role'), nullable=False, default='Resident')
    apartment_id = db.Column(db.Integer, db.ForeignKey('apartment.id'), nullable=True)
    lessee_id = db.Column(db.Integer, db.ForeignKey('lessee.id'), nullable=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=True)  

    def get_reset_token(self):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod 
    def verify_reset_token(token, max_age = 1800):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=max_age)
            user_id = data.get('user_id')
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"<User {self.username} ({self.role}), Lessee ID: {self.lessee_id}, Apartment ID: {self.apartment_id}, Property_id = {self.property_id}>"

class Lease(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    apartment_id = db.Column(db.Integer, db.ForeignKey('apartment.id'), nullable=False)
    lessee_id = db.Column(db.Integer, db.ForeignKey('lessee.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    monthly_rent = db.Column(db.Numeric(10, 2), nullable=False)
    next_due_date = db.Column(db.Date, nullable=True)
    lease_document_url = db.Column(db.String(255), nullable=True)

    # Relationship: Lease -> Payments
    payments = db.relationship('Payment', backref='lease', lazy=True)

    def __init__(self, start_date, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.next_due_date = start_date + timedelta(days=30)
        self.end_date = start_date + timedelta(days=365)

    def __repr__(self):
        return f"<Lease ID: {self.id}, Lessee ID: {self.lessee_id}, Apartment ID: {self.apartment_id}>"

class Payment(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    lease_id = db.Column(db.Integer, db.ForeignKey('lease.id'), nullable=False)
    rent_amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    payment_method = db.Column(db.Enum('Bank', 'Credit/Debit Card', name='payment_methods'), nullable=False)
    processing_fee = db.Column(db.Numeric(10, 2), nullable=True)
    total_amount = db.Column(db.Numeric(10, 2), nullable = False)
    status = db.Column(db.Enum('Pending', 'Completed', name='payment_statuses'), nullable=False, default='Pending')

    def __repr__(self):
        return f"<Payment ID: {self.id}, Lease ID: {self.lease_id}, Amount: {self.total_amount}>"

class MaintenanceRequest(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    apartment_id = db.Column(db.Integer, db.ForeignKey('apartment.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=True)  
    category = db.Column(db.Enum('Plumbing', 'Electrical', 'Appliances', 'Hardware', 'Fire/Security', name='maintenance_categories'), nullable=False)
    severity = db.Column(db.Enum('Low', 'Medium', 'High', name='severity_levels'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('Open', 'In Progress', 'Deferred', 'Closed', name='request_statuses'), nullable=False, default='Open')
    admin_comments = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<MaintenanceRequest ID: {self.id}, Apartment ID: {self.apartment_id}, Property ID: {self.property_id}, Category: {self.category}, Status: {self.status}>"

class Lessee(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    apartment_id = db.Column(db.Integer, db.ForeignKey('apartment.id'), nullable=False)
    mobile_number = db.Column(db.String(15), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    monthly_rent = db.Column(db.Numeric(10, 2), nullable=False)

    user = db.relationship('User', backref='lessee', uselist=False, lazy=True)

    lease = db.relationship('Lease', backref='lessee', uselist=False, lazy=True)

    def __repr__(self):
        return f"<Lessee {self.first_name} {self.last_name}, Apartment: {self.apartment_id}, Property: {self.property_id}>"
    
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Notif id: {self.id}, user id: {self.user_id}, Message: {self.message}>"
