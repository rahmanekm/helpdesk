from flask import render_template, redirect, url_for, flash, request, Blueprint
from flask_login import login_required, current_user
from . import bp
from .. import db
from ..models import Subscription, User
from .forms import SubscriptionForm
from datetime import datetime

@bp.route('/')
@login_required
def list_subscriptions():
    subscriptions = Subscription.query.all()
    return render_template('subscriptions/list.html', subscriptions=subscriptions)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_subscription():
    form = SubscriptionForm()
    form.assigned_to_id.choices = [(user.id, user.username) for user in User.query.order_by('username').all()]
    form.assigned_to_id.choices.insert(0, (0, 'None')) # Add a 'None' option
    
    if form.validate_on_submit():
        assigned_to_user = None
        if form.assigned_to_id.data != 0:
            assigned_to_user = User.query.get(form.assigned_to_id.data)

        subscription = Subscription(
            name=form.name.data,
            vendor=form.vendor.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            renewal_date=form.renewal_date.data,
            cost=form.cost.data,
            frequency=form.frequency.data,
            status=form.status.data,
            notes=form.notes.data,
            assigned_to=assigned_to_user
        )
        db.session.add(subscription)
        db.session.commit()
        flash('Subscription created successfully!', 'success')
        return redirect(url_for('subscriptions.list_subscriptions'))
    return render_template('subscriptions/create.html', form=form)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_subscription(id):
    subscription = Subscription.query.get_or_404(id)
    form = SubscriptionForm(obj=subscription)
    form.assigned_to_id.choices = [(user.id, user.username) for user in User.query.order_by('username').all()]
    form.assigned_to_id.choices.insert(0, (0, 'None')) # Add a 'None' option

    if request.method == 'POST' and form.validate_on_submit():
        assigned_to_user = None
        if form.assigned_to_id.data != 0:
            assigned_to_user = User.query.get(form.assigned_to_id.data)

        subscription.name = form.name.data
        subscription.vendor = form.vendor.data
        subscription.start_date = form.start_date.data
        subscription.end_date = form.end_date.data
        subscription.renewal_date = form.renewal_date.data
        subscription.cost = form.cost.data
        subscription.frequency = form.frequency.data
        subscription.status = form.status.data
        subscription.notes = form.notes.data
        subscription.assigned_to = assigned_to_user
        subscription.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Subscription updated successfully!', 'success')
        return redirect(url_for('subscriptions.list_subscriptions'))
    elif request.method == 'GET':
        if subscription.assigned_to:
            form.assigned_to_id.data = subscription.assigned_to.id
        else:
            form.assigned_to_id.data = 0
    return render_template('subscriptions/edit.html', form=form, subscription=subscription)

@bp.route('/view/<int:id>')
@login_required
def view_subscription(id):
    subscription = Subscription.query.get_or_404(id)
    return render_template('subscriptions/view.html', subscription=subscription)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_subscription(id):
    subscription = Subscription.query.get_or_404(id)
    db.session.delete(subscription)
    db.session.commit()
    flash('Subscription deleted successfully!', 'success')
    return redirect(url_for('subscriptions.list_subscriptions'))
