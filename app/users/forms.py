from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from ..models import User

class UserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    role = SelectField('Role', choices=[
        ('customer', 'Customer'),
        ('agent', 'Agent'),
        ('admin', 'Admin')
    ], validators=[DataRequired()])
    department = StringField('Department', validators=[Length(max=64)])
    organization = StringField('Organization', validators=[Length(max=100)])
    phone = StringField('Phone', validators=[Length(max=20)])
    is_active = BooleanField('Active')
    submit = SubmitField('Save')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user and (not hasattr(self, 'user') or user.id != self.user.id):
            raise ValidationError('Email already registered.')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user and (not hasattr(self, 'user') or user.id != self.user.id):
            raise ValidationError('Username already taken.')

class PasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Set Password')

class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class PasswordResetForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')