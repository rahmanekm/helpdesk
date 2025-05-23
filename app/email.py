from flask import current_app, render_template
from flask_mail import Message
from . import mail

def send_email(subject, recipients, text_body, html_body):
    msg = Message(subject, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg) 