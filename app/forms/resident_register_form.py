from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, ValidationError
from app.models import User

class ResidentRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message="Username cannot be blank"), Length(min=5, max=30, message="Must be minimum %(min)d and maximum %(max)d characters long")])
    
    email = StringField('Email', validators=[DataRequired(message="Email cannot be blank"), Email(), Length(max=100)])

    password = PasswordField('Password', validators=[DataRequired(message="Password cannot be blank"), Length(min=8, message="Must be at least %(min)d characters long")])

    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(message="Confirm Password cannot be blank"), EqualTo('password', message="Password and Confirm Password values must match")])

    registered_mobile = StringField('Registered Mobile Number', validators=[DataRequired(message="Mobile number cannot be blank"), Length(min=10, max=15, message="Mobile number must be between %(min)d and %(max)d characters long"), Regexp(r'^\+?[0-9\s\-]+$', message="Enter a valid mobile number (digits, spaces, dashes, optional +)")])
    
    apartment_number = IntegerField('Apartment/Unit Number', validators=[DataRequired(message="Apartment Number cannot be blank")])

    last_name = StringField('Last Name', validators=[DataRequired(message="Last name cannot be blank")])

    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username taken. Please choose a different one.')
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please log in.')