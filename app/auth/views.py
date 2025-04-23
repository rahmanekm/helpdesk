from flask import render_template, redirect, request, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm, RegistrationForm, RegistrationPasswordForm

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        flash('Invalid email or password.')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Check if registration password is verified
    if not session.get('registration_verified'):
        form = RegistrationPasswordForm()
        if form.validate_on_submit():
            if form.registration_password.data == "Forefrontcsez@999":
                session['registration_verified'] = True
                session.permanent = True  # Make the session permanent
                return redirect(url_for('auth.register'))
            flash('Invalid registration password.', 'error')
        return render_template('auth/register_password.html', form=form)
    
    # If we get here, the user has verified the password
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                   username=form.username.data,
                   role='user')
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        # Clear the registration verification
        session.pop('registration_verified', None)
        flash('You can now login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form) 