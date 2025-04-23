from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, FloatField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class AssetForm(FlaskForm):
    name = StringField('Name', validators=[
        DataRequired(),
        Length(max=100)
    ])
    asset_type = SelectField('Type', choices=[
        ('Hardware', 'Hardware'),
        ('Software', 'Software'),
        ('Network', 'Network'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Maintenance', 'Maintenance'),
        ('Retired', 'Retired')
    ], validators=[DataRequired()])
    purchase_date = DateField('Purchase Date', validators=[Optional()])
    warranty_end = DateField('Warranty End', validators=[Optional()])
    cost = FloatField('Cost', validators=[Optional()])
    location = StringField('Location', validators=[
        Optional(),
        Length(max=100)
    ])
    serial_number = StringField('Serial Number', validators=[
        Optional(),
        Length(max=100)
    ])
    model = StringField('Model', validators=[
        Optional(),
        Length(max=100)
    ])
    manufacturer = StringField('Manufacturer', validators=[
        Optional(),
        Length(max=100)
    ])
    assigned_to = SelectField('Assigned To', coerce=int, validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save') 