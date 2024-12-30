from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, NumberRange

class PaymentForm(FlaskForm):

    payment_method = SelectField(
        'Payment Method', 
        choices=[('Bank Account', 'Bank Account'), ('Credit/Debit Card', 'Credit/Debit Card')],
        validators=[DataRequired()]
    )

    submit = SubmitField('Make Payment')
