from flask import render_template, redirect, url_for
from flask_login import current_user, login_required
from . import main
from app.models import Ticket, Article, TicketStatus, Category
from sqlalchemy import desc, and_
from datetime import datetime

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    # Get recent tickets
    recent_tickets = Ticket.query.filter(
        (Ticket.submitter_id == current_user.id) | 
        (Ticket.assigned_agent_id == current_user.id)
    ).order_by(desc(Ticket.created_at)).limit(5).all()
    
    # Get recent articles
    recent_articles = Article.query.filter_by(status='Published').order_by(
        desc(Article.created_at)
    ).limit(3).all()
    
    # Get statistics
    total_tickets = Ticket.query.count()
    open_tickets = Ticket.query.join(TicketStatus).filter(TicketStatus.is_closed == False).count()
    my_tickets = Ticket.query.filter_by(assigned_agent_id=current_user.id).count()
    overdue_tickets = Ticket.query.filter(Ticket.due_date < datetime.utcnow()).count()
    
    # Get ticket statistics by category
    categories = Category.query.all()
    category_stats = []
    for category in categories:
        stats = {
            'name': category.name,
            'total': Ticket.query.filter_by(category_id=category.id).count(),
            'open': Ticket.query.join(TicketStatus).filter(
                and_(
                    Ticket.category_id == category.id,
                    TicketStatus.is_closed == False
                )
            ).count()
        }
        category_stats.append(stats)
    
    return render_template('main/dashboard.html',
                         recent_tickets=recent_tickets,
                         recent_articles=recent_articles,
                         total_tickets=total_tickets,
                         open_tickets=open_tickets,
                         my_tickets=my_tickets,
                         overdue_tickets=overdue_tickets,
                         category_stats=category_stats) 