from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, DateField, FloatField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Optional

class OfficeInventoryForm(FlaskForm):
    item_name = StringField('Item Name', validators=[DataRequired(), Length(min=2, max=100)])
    category = StringField('Category', validators=[Length(max=50), Optional()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    location = StringField('Location', validators=[Length(max=100), Optional()])
    purchase_date = DateField('Purchase Date', format='%Y-%m-%d', validators=[Optional()])
    cost = FloatField('Cost', validators=[Optional()])
    status = SelectField('Status', choices=[('In Use', 'In Use'), ('Available', 'Available'), ('Damaged', 'Damaged'), ('Retired', 'Retired')], validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Length(max=500), Optional()])
    assigned_to_id = SelectField('Assigned To (User ID)', coerce=int, validators=[Optional()])
    submit = SubmitField('Submit')
