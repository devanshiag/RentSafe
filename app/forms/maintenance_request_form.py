from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class MaintenanceRequestForm(FlaskForm):
    severity = SelectField('Severity', choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')],
        validators=[DataRequired(message="Please choose the severity of the issue")])
    
    category = SelectField('Category',choices=[('Plumbing', 'Plumbing'), ('Electrical', 'Electrical'),
            ('Appliances', 'Appliances'), ('Hardware', 'Hardware'), ('Fire/Security', 'Fire/Security')],
        validators=[DataRequired()])
    
    description = TextAreaField('Brief Description', validators=[DataRequired(message="Please enter a short description of the issue"), Length(min=10, max=500)])
    
    submit = SubmitField('Submit Request')
