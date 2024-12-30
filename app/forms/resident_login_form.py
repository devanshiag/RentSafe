from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class ResidentLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message= "Username cannot be empty")])
    password = PasswordField('Password', validators=[DataRequired(message="Password cannot be empty")])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')