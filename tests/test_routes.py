import unittest
from datetime import datetime
from decimal import Decimal
import sys

from app import app, db, bcrypt
from app.models import User, Property, Apartment, Lessee, Lease, Payment, MaintenanceRequest
from flask_login import current_user

class TestAppRoutes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Configure the app for testing
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        cls.client = app.test_client()
        cls.app_context = app.app_context()
        cls.app_context.push()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        # Create test data
        property = Property(name="Test Property", address="123 Test St")
        db.session.add(property)
        db.session.commit()

        apartment = Apartment(property_id=property.id)
        db.session.add(apartment)
        db.session.commit()

        lessee = Lessee(first_name="John", last_name="Doe", mobile_number="1234567890", apartment_id=apartment.id, property_id=property.id, monthly_rent = 1000)
        db.session.add(lessee)
        db.session.commit()

        lease = Lease(apartment_id=apartment.id, lessee_id=lessee.id, start_date=datetime(2023, 1, 1), monthly_rent=1000)
        db.session.add(lease)
        db.session.commit()

        admin = User(username="admin", password_hash='admin123', email="admin@test.com", role="Admin", mobile_number = "9297929229", property_id=property.id, apartment_id = apartment.id, lessee_id = lessee.id)
        db.session.add(admin)
        db.session.commit()

    def tearDown(self):
        db.session.query(Payment).delete()
        db.session.query(MaintenanceRequest).delete()
        db.session.query(Lease).delete()
        db.session.query(Lessee).delete()
        db.session.query(Apartment).delete()
        db.session.query(Property).delete()
        db.session.query(User).delete()
        db.session.commit()


    def test_home_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome", response.data)

    # UI Test: Admin Dashboard Access Restriction
    def test_admin_dashboard_access_restriction(self):
        response = self.client.get('/admin/dashboard', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You are logged out', response.data)

    # Backend Test: Resident Registration
    def test_resident_registration(self):
        with app.app_context():
            lessee = Lessee(first_name="John", last_name="Doe", mobile_number="1234567890", apartment_id=1, property_id=1, monthly_rent = 1000)
            db.session.add(lessee)
            db.session.commit()

        response = self.client.post('/resident/register', data={
            "username": "johndoe",
            "password": "password",
            "confirm_password": "password",
            "email": "johndoe@example.com",
            "registered_mobile": "1234567890",
            "apartment_number": 1,
            "last_name": "Doe"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your account has been created', response.data)

    def test_admin_login_successful(self):
        admin = User.query.filter_by(username="admin").first()
        self.assertIsNotNone(admin, "Admin user not found in test database.")

        response = self.client.post('/admin/login', data={
            'username': "admin",
            'password': "admin123"
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200, "Login response status code is not 200.")


    def test_admin_login_unsuccessful(self):
        response = self.client.post('/admin/login', data=dict(username="admin", password="wrongpassword"), follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_rent_report_access_denied_for_residents(self):
        hashed_password = bcrypt.generate_password_hash("resident123").decode('utf-8')
        resident = User(username="resident", password_hash=hashed_password, email="resident@test.com", role="Resident", mobile_number = "1234567890", apartment_id = 1, property_id = 1, lessee_id = 1)
        db.session.add(resident)
        db.session.commit()
        
        self.client.post('/admin/login', data=dict(username="resident", password="resident123"), follow_redirects=True)
        response = self.client.get('/admin/rent-report')
        self.assertEqual(response.status_code, 302)

    # Service Test: Notification Fetching
    def test_fetch_notifications(self):
        user = User(username="resident", 
                    password_hash=bcrypt.generate_password_hash("password").decode('utf-8'),
                    email='resident@test.com', 
                    mobile_number='1234567890', 
                    role='Resident', 
                    apartment_id=1, 
                    lessee_id=1, 
                    property_id=1)
        db.session.add(user)
        db.session.commit()

        with self.client as client:
            response = client.post('/resident/login', 
                                   data=dict(username="resident", password="password"), 
                                   follow_redirects=True)
            self.assertEqual(response.status_code, 200)

            response = client.get('/notifications')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Notifications', response.data)

    def test_make_payment(self):
        hashed_password = bcrypt.generate_password_hash("resident123").decode('utf-8')
        resident = User(username="resident", password_hash=hashed_password, email="resident@test.com", role="Resident", mobile_number="1234567890", apartment_id=1, property_id=1, lessee_id=1)
        db.session.add(resident)
        db.session.commit()

        monthly_rent = 1000
        processing_fee = monthly_rent * Decimal('0.028')
        total_amount = monthly_rent + processing_fee

        self.client.post('/resident/login', data=dict(username="resident", password="resident123"), follow_redirects=True)
        
        response = self.client.post('/resident/payment', data=dict(payment_method="Credit/Debit Card"), follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # Check that the success message includes the correct amount
        success_message = f"Payment of ₹{total_amount:.2f} successful!"
        self.assertIn(success_message.encode(), response.data)


    def test_create_maintenance_request(self):
        hashed_password = bcrypt.generate_password_hash("resident123").decode('utf-8')
        resident = User(username="resident", password_hash=hashed_password, email="resident@test.com", role="Resident",mobile_number = "1234567890", apartment_id = 1, property_id = 1, lessee_id = 1)
        db.session.add(resident)
        db.session.commit()

        self.client.post('/resident/login', data=dict(username="resident", password="resident123"), follow_redirects=True)
        response = self.client.post('/resident/new_request', data=dict(severity="High", category="Plumbing", description="Leaking faucet"), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Your maintenance request has been submitted successfully!", response.data)

    def test_view_open_requests(self):
        hashed_password = bcrypt.generate_password_hash("resident123").decode('utf-8')
        resident = User(username="resident", password_hash=hashed_password, email="resident@test.com", role="Resident",mobile_number = "1234567890", apartment_id = 1, property_id = 1, lessee_id = 1)
        db.session.add(resident)
        db.session.commit()

        maintenance_request = MaintenanceRequest(user_id=resident.id, apartment_id=1, property_id=1, severity="High", category="Plumbing", description="Leaking faucet", status="Open")
        db.session.add(maintenance_request)
        db.session.commit()

        self.client.post('/resident/login', data=dict(username="resident", password="resident123"), follow_redirects=True)
        response = self.client.get('/resident/open_requests')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Open Requests", response.data)

if __name__ == '__main__':
    unittest.main()
