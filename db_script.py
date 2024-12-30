from app import db
from app.models import Property, Apartment, Lessee, Lease, User

from datetime import date

# Create property
property1 = Property(name="Ganga Valley Apartments", address="117 Ganga Sideways, Kanpur")
db.session.add(property1)
db.session.commit()


# Create apartments
apartment1 = Apartment(property_id=property1.id)
db.session.add(apartment1)
db.session.commit()

apartment2 = Apartment(property_id=property1.id)
db.session.add(apartment2)
db.session.commit()

apartment3 = Apartment(property_id=property1.id)
db.session.add(apartment3)
db.session.commit()


# Create lessees
lessee1 = Lessee(property_id = property1.id, apartment_id = apartment1.id, mobile_number = '9191919191', first_name = 'Devanshi', last_name = 'Agarwal', monthly_rent = 20000.00)
db.session.add(lessee1)
db.session.commit()

lessee2 = Lessee(property_id = property1.id, apartment_id = apartment2.id, mobile_number = '9292929292', first_name = 'Navya', last_name = 'Sharma', monthly_rent = 10000.00)
db.session.add(lessee2)
db.session.commit()

lessee3 = Lessee(property_id = property1.id, apartment_id = apartment3.id, mobile_number = '9393939393', first_name = 'Harsh', last_name = 'Agrawal', monthly_rent = 8000.00)
db.session.add(lessee3)
db.session.commit()


# Create leases
lease1 = Lease(apartment_id=apartment1.id, lessee_id=lessee1.id, start_date=date(2024, 10, 4),  monthly_rent=20000.00, lease_document_url="./app/static/lease_documents/LEASE AGREEMENT.pdf"
)
db.session.add(lease1)
db.session.commit()

lease2 = Lease(apartment_id=apartment2.id, lessee_id=lessee2.id, start_date=date(2024, 8, 5),  monthly_rent=10000.00, lease_document_url="./app/static/lease_documents/Rent-Agreement-2.pdf"
)
db.session.add(lease2)
db.session.commit()

lease3 = Lease(apartment_id=apartment3.id, lessee_id=lessee3.id, start_date=date(2024, 9, 6),  monthly_rent=8000.00, lease_document_url="./app/static/lease_documents/Rent-Agreement-2.pdf"
)
db.session.add(lease3)
db.session.commit()


#Create an admin for property 1
admin1 = User(username = 'admin_ganga', password_hash = 'admin123', email = 'agrdevanshi@gmail.com', mobile_number = '1234567890', role = 'Admin', property_id = property1.id)
db.session.add(admin1)
db.session.commit()

# Users, Maintenance Requests, Payments and Notifications can be added from UI