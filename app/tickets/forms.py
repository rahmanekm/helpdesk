from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, SubmitField, BooleanField, SelectMultipleField, DateTimeField
from wtforms.validators import DataRequired, Length, Optional
from ..models import User, Category, TicketPriority, TicketStatus, Asset, Ticket

class TicketForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired(), Length(1, 200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    priority = SelectField('Priority', coerce=int, validators=[DataRequired()])
    status = SelectField('Status', coerce=int, validators=[DataRequired()])
    assigned_to = SelectField('Assign To', coerce=int, validators=[Optional()])
    due_date = DateTimeField('Due Date', format='%Y-%m-%d %H:%M', validators=[Optional()])
    assets = SelectMultipleField('Related Assets', coerce=int)
    tags = StringField('Tags (comma separated)')
    attachments = FileField('Attachments', render_kw={'multiple': True})
    
    def __init__(self, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)
        self.category.choices = [(c.id, c.name) for c in Category.query.order_by('name')]
        self.priority.choices = [(p.id, p.name) for p in TicketPriority.query.order_by('name')]
        self.status.choices = [(s.id, s.name) for s in TicketStatus.query.order_by('name')]
        self.assets.choices = [(a.id, f"{a.name} ({a.type})") for a in Asset.query.order_by('name')]

class TicketFilterForm(FlaskForm):
    status = SelectField('Status', coerce=int, validators=[Optional()])
    priority = SelectField('Priority', coerce=int, validators=[Optional()])
    category = SelectField('Category', coerce=int, validators=[Optional()])
    assigned_to = SelectField('Assigned To', coerce=int, validators=[Optional()])
    date_range = SelectField('Date Range', choices=[
        ('', 'All Time'),
        ('today', 'Today'),
        ('week', 'This Week'),
        ('month', 'This Month'),
        ('custom', 'Custom Range')
    ])
    start_date = DateTimeField('Start Date', format='%Y-%m-%d', validators=[Optional()])
    end_date = DateTimeField('End Date', format='%Y-%m-%d', validators=[Optional()])
    tags = StringField('Tags')
    search = StringField('Search')

class MergeTicketForm(FlaskForm):
    target_ticket = SelectField('Merge Into Ticket', coerce=int, validators=[DataRequired()])
    
    def __init__(self, *args, exclude_id=None, **kwargs):
        super(MergeTicketForm, self).__init__(*args, **kwargs)
        query = Ticket.query
        if exclude_id:
            query = query.filter(Ticket.id != exclude_id)
        self.target_ticket.choices = [(t.id, f"#{t.id} - {t.subject}") for t in query.order_by(Ticket.created_at.desc())]

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    is_internal = SelectField('Visibility', choices=[
        ('0', 'Public - Visible to requester'),
        ('1', 'Internal - Staff only')
    ], default='0')
    attachments = FileField('Attachments', render_kw={'multiple': True})

class CustomFieldForm(FlaskForm):
    name = StringField('Field Name', validators=[DataRequired(), Length(1, 100)])
    field_type = SelectField('Field Type', choices=[
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('select', 'Select'),
        ('checkbox', 'Checkbox'),
        ('textarea', 'Text Area')
    ])
    is_required = SelectField('Required', choices=[('0', 'No'), ('1', 'Yes')])
    options = TextAreaField('Options (one per line, for Select type)')

class TicketUpdateForm(FlaskForm):
    status = SelectField('Status', coerce=int)
    assigned_to = SelectField('Assign to', coerce=int, validators=[Optional()])
    priority = SelectField('Priority', coerce=int)
    submit = SubmitField('Update Ticket')

    def __init__(self, *args, **kwargs):
        super(TicketUpdateForm, self).__init__(*args, **kwargs)
        self.status.choices = [(s.id, s.name) for s in TicketStatus.query.order_by('name')]
        self.priority.choices = [(p.id, p.name) for p in TicketPriority.query.order_by('name')]
        self.assigned_to.choices = [(0, 'Unassigned')] + [
            (user.id, user.username) for user in User.query.all()
        ] 