from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, FloatField, TextAreaField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Email, Optional
from app.models import User

class AssetForm(FlaskForm):
    name = StringField('Asset Name', validators=[DataRequired()])
    asset_type = SelectField('Asset Type', validators=[DataRequired()], choices=[
        ('Hardware', 'Hardware'),
        ('Software', 'Software'),
        ('Network', 'Network'),
        ('Peripheral', 'Peripheral'),
        ('Other', 'Other')
    ])
    status = SelectField('Status', validators=[DataRequired()], choices=[
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Maintenance', 'Maintenance'),
        ('Retired', 'Retired')
    ])
    serial_number = StringField('Serial Number', validators=[DataRequired()])
    model = StringField('Model')
    manufacturer = StringField('Manufacturer')
    purchase_date = DateField('Purchase Date')
    warranty_end = DateField('Warranty End Date')
    cost = FloatField('Cost')
    location = StringField('Location')
    assigned_to = SelectField('Assigned To', coerce=int)
    notes = TextAreaField('Notes')
    submit = SubmitField('Save Asset')

    def __init__(self, *args, **kwargs):
        super(AssetForm, self).__init__(*args, **kwargs)
        self.assigned_to.choices = [(0, 'Unassigned')] + [(user.id, user.username) 
            for user in User.query.order_by(User.username).all()]

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Optional(), Length(min=6)])
    role = SelectField('Role', choices=[
        ('user', 'User'),
        ('agent', 'Agent'),
        ('admin', 'Admin')
    ])
    department = StringField('Department')
    organization = StringField('Organization')
    phone = StringField('Phone')
    is_active = BooleanField('Active')
    submit = SubmitField('Save User')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        if not kwargs.get('obj'):
            self.password.validators = [DataRequired(), Length(min=6)] 