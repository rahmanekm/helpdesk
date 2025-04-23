from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from ..models import User, db, AuditLog
from .forms import UserForm, PasswordForm, PasswordResetRequestForm, PasswordResetForm
from ..decorators import admin_required
from ..email import send_email
import secrets
from ..utils import get_client_ip

bp = Blueprint('users', __name__)

@bp.route('/users')
@login_required
@admin_required
def list_users():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('users/list.html', users=users)

@bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    form = UserForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            username=form.username.data,
            role=form.role.data,
            department=form.department.data,
            organization=form.organization.data,
            phone=form.phone.data,
            is_active=form.is_active.data
        )
        # Generate a random password
        temp_password = secrets.token_urlsafe(8)
        user.set_password(temp_password)
        
        db.session.add(user)
        db.session.commit()
        
        # Send email with temporary password
        send_email(
            subject='Your Helpdesk Account',
            recipients=[user.email],
            text_body=render_template('email/new_user.txt', user=user, password=temp_password),
            html_body=render_template('email/new_user.html', user=user, password=temp_password)
        )
        
        flash('User created successfully. A temporary password has been sent to their email.', 'success')
        return redirect(url_for('.list_users'))
    return render_template('users/create.html', form=form)

@bp.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    form.user = user  # For validation
    
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.role = form.role.data
        user.department = form.department.data
        user.organization = form.organization.data
        user.phone = form.phone.data
        user.is_active = form.is_active.data
        
        db.session.commit()
        flash('User updated successfully.', 'success')
        return redirect(url_for('.list_users'))
    return render_template('users/edit.html', form=form, user=user)

@bp.route('/users/<int:id>/password', methods=['GET', 'POST'])
@login_required
@admin_required
def set_password(id):
    user = User.query.get_or_404(id)
    form = PasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Password has been updated.', 'success')
        return redirect(url_for('.list_users'))
    return render_template('users/password.html', form=form, user=user)

@bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.get_reset_password_token()
            send_email(
                subject='Reset Your Password',
                recipients=[user.email],
                text_body=render_template('email/reset_password.txt', user=user, token=token),
                html_body=render_template('email/reset_password.html', user=user, token=token)
            )
        flash('Check your email for the instructions to reset your password.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('users/reset_password_request.html', form=form)

@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('users/reset_password.html', form=form)

@bp.route('/users/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    
    # Don't allow deleting the last admin
    if user.role == 'admin' and User.query.filter_by(role='admin').count() <= 1:
        flash('Cannot delete the last admin user.', 'danger')
        return redirect(url_for('.list_users'))
    
    # Create audit log
    log = AuditLog(
        action='delete',
        entity_type='user',
        entity_id=user.id,
        user_id=current_user.id,
        changes={'username': user.username, 'email': user.email, 'role': user.role},
        ip_address=get_client_ip()
    )
    db.session.add(log)
    
    # Delete the user
    db.session.delete(user)
    db.session.commit()
    
    flash('User has been deleted successfully.', 'success')
    return redirect(url_for('.list_users'))