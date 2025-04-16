import os
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from . import tickets
from .. import db, mail
from ..models import Ticket, Comment, Attachment, User
from .forms import TicketForm, CommentForm, TicketUpdateForm
from flask_mail import Message

@tickets.route('/submit', methods=['GET', 'POST'])
@login_required
def submit_ticket():
    form = TicketForm()
    if form.validate_on_submit():
        ticket = Ticket(
            subject=form.subject.data,
            category=form.category.data,
            priority=form.priority.data,
            description=form.description.data,
            submitter=current_user
        )
        db.session.add(ticket)
        
        # Handle file attachment
        if form.attachment.data:
            file = form.attachment.data
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            attachment = Attachment(
                filename=filename,
                file_path=file_path,
                file_type=file.content_type,
                file_size=os.path.getsize(file_path),
                ticket=ticket
            )
            db.session.add(attachment)
        
        db.session.commit()
        
        # Send notification email
        msg = Message('New Support Ticket Submitted',
                     sender=current_app.config['MAIL_DEFAULT_SENDER'],
                     recipients=[current_user.email])
        msg.body = f'''
        Your ticket has been submitted successfully.
        Ticket ID: {ticket.id}
        Subject: {ticket.subject}
        Category: {ticket.category}
        Priority: {ticket.priority}
        
        You can view your ticket at: {url_for('tickets.view_ticket', ticket_id=ticket.id, _external=True)}
        '''
        mail.send(msg)
        
        flash('Your ticket has been submitted successfully!')
        return redirect(url_for('tickets.view_ticket', ticket_id=ticket.id))
    return render_template('tickets/submit.html', form=form)

@tickets.route('/ticket/<int:ticket_id>')
@login_required
def view_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if not (current_user.role in ['agent', 'admin'] or ticket.submitter == current_user):
        flash('You do not have permission to view this ticket.')
        return redirect(url_for('main.index'))
    
    comment_form = CommentForm()
    update_form = TicketUpdateForm() if current_user.role in ['agent', 'admin'] else None
    
    if update_form:
        update_form.status.data = ticket.status
        update_form.assigned_agent.data = ticket.assigned_agent_id
        update_form.priority.data = ticket.priority
    
    return render_template('tickets/view.html',
                         ticket=ticket,
                         comment_form=comment_form,
                         update_form=update_form)

@tickets.route('/ticket/<int:ticket_id>/update', methods=['POST'])
@login_required
def update_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if current_user.role not in ['agent', 'admin']:
        flash('You do not have permission to update this ticket.')
        return redirect(url_for('main.index'))
    
    form = TicketUpdateForm()
    if form.validate_on_submit():
        ticket.status = form.status.data
        ticket.assigned_agent_id = form.assigned_agent.data if form.assigned_agent.data != 0 else None
        ticket.priority = form.priority.data
        
        db.session.commit()
        flash('Ticket updated successfully.')
    
    return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))

@tickets.route('/ticket/<int:ticket_id>/comment', methods=['POST'])
@login_required
def add_comment(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if not (current_user.role in ['agent', 'admin'] or ticket.submitter == current_user):
        flash('You do not have permission to comment on this ticket.')
        return redirect(url_for('main.index'))
    
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            is_internal=form.is_internal.data and current_user.role in ['agent', 'admin'],
            ticket=ticket,
            author=current_user
        )
        db.session.add(comment)
        db.session.commit()
        
        # Send notification email
        recipients = set()
        if ticket.submitter != current_user:
            recipients.add(ticket.submitter.email)
        if ticket.assigned_agent and ticket.assigned_agent != current_user:
            recipients.add(ticket.assigned_agent.email)
        
        if recipients:
            msg = Message(f'New Comment on Ticket #{ticket.id}',
                         sender=current_app.config['MAIL_DEFAULT_SENDER'],
                         recipients=list(recipients))
            msg.body = f'''
            A new comment has been added to ticket #{ticket.id}:
            
            {comment.content}
            
            View the ticket at: {url_for('tickets.view_ticket', ticket_id=ticket.id, _external=True)}
            '''
            mail.send(msg)
        
        flash('Your comment has been added.')
    
    return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))

@tickets.route('/dashboard')
@login_required
def dashboard():
    if current_user.role in ['agent', 'admin']:
        tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
    else:
        tickets = current_user.submitted_tickets.order_by(Ticket.created_at.desc()).all()
    
    return render_template('tickets/dashboard.html', tickets=tickets) 