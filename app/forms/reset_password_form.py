from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length, EqualTo

from app.models import User

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(message="Password cannot be blank"), Length(min=8, message="Must be at least %(min)d characters long")])

    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(message="Confirm Password cannot be blank"), EqualTo('password', message="Password and Confirm Password values must match")])

    submit = SubmitField('Reset Password')