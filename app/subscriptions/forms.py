from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, DateField, FloatField, SelectField
from wtforms.validators import DataRequired, Length, Email, Optional
from datetime import date

class SubscriptionForm(FlaskForm):
    name = StringField('Subscription Name', validators=[DataRequired(), Length(min=2, max=100)])
    vendor = StringField('Vendor', validators=[Length(max=100), Optional()])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[Optional()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[Optional()])
    renewal_date = DateField('Renewal Date', format='%Y-%m-%d', validators=[Optional()])
    cost = FloatField('Cost', validators=[Optional()])
    frequency = SelectField('Frequency', choices=[('monthly', 'Monthly'), ('annually', 'Annually'), ('quarterly', 'Quarterly'), ('one-time', 'One-time')], validators=[Optional()])
    status = SelectField('Status', choices=[('Active', 'Active'), ('Expired', 'Expired'), ('Pending Renewal', 'Pending Renewal'), ('Cancelled', 'Cancelled')], validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Length(max=500), Optional()])
    assigned_to_id = SelectField('Assigned To (User ID)', coerce=int, validators=[Optional()])
    submit = SubmitField('Submit')
