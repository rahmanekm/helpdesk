from flask import render_template
from flask_login import login_required, current_user
from . import main
from ..models import Ticket

@main.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role in ['agent', 'admin']:
            tickets = Ticket.query.order_by(Ticket.created_at.desc()).limit(5).all()
        else:
            tickets = current_user.submitted_tickets.order_by(Ticket.created_at.desc()).limit(5).all()
        return render_template('main/index.html', tickets=tickets)
    return render_template('main/index.html') 