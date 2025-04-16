from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length
from ..models import User

class TicketForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired(), Length(1, 200)])
    category = SelectField('Category', choices=[
        ('Hardware', 'Hardware'),
        ('Software', 'Software'),
        ('Network', 'Network'),
        ('Email', 'Email'),
        ('Access', 'Access Control'),
        ('Other', 'Other')
    ])
    priority = SelectField('Priority', choices=[
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical')
    ])
    description = TextAreaField('Description', validators=[DataRequired()])
    attachment = FileField('Attachment', validators=[
        FileAllowed(['png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt', 'log'],
                   'Only images, PDFs, and documents are allowed.')
    ])
    submit = SubmitField('Submit Ticket')

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    is_internal = BooleanField('Internal Note (visible only to agents)')
    submit = SubmitField('Add Comment')

class TicketUpdateForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('Open', 'Open'),
        ('Assigned', 'Assigned'),
        ('In Progress', 'In Progress'),
        ('Pending User Response', 'Pending User Response'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed')
    ])
    assigned_agent = SelectField('Assign to', coerce=int)
    priority = SelectField('Priority', choices=[
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical')
    ])
    submit = SubmitField('Update Ticket')

    def __init__(self, *args, **kwargs):
        super(TicketUpdateForm, self).__init__(*args, **kwargs)
        self.assigned_agent.choices = [(0, 'Unassigned')] + [
            (user.id, user.username) for user in User.query.filter_by(role='agent').all()
        ] 