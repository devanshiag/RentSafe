from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message="Username cannot be empty"), Length(min=5, max=20, message="Must be minimum %(min)d and maximum %(max)d characters long")])
    password = PasswordField('Password', validators=[DataRequired(message="Password cannot be empty")])
    submit = SubmitField('Login', validators=[DataRequired()])