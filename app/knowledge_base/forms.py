from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, FileField
from wtforms.validators import DataRequired, Length, Optional
from ..models import Category

class ArticleForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(),
        Length(max=200)
    ])
    content = TextAreaField('Content', validators=[
        DataRequired()
    ])
    category = SelectField('Category', coerce=int, validators=[Optional()])
    status = SelectField('Status', choices=[
        ('Draft', 'Draft'),
        ('Published', 'Published'),
        ('Archived', 'Archived')
    ], validators=[DataRequired()])
    tags = StringField('Tags', validators=[Optional()])
    attachments = FileField('Attachments')
    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.category.choices = [(c.id, c.name) for c in Category.query.order_by('name')]

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Post Comment') 