from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import bp
from .. import db
from ..models import Subscription, User, SubscriptionRenewalLog
from .forms import SubscriptionForm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from ..utils import get_client_ip


@bp.route('/')
@login_required
def list_subscriptions():
    subscriptions = Subscription.query.all()
    return render_template(
        'subscriptions/list.html',
        subscriptions=subscriptions,
        timedelta=timedelta,
        relativedelta=relativedelta,
        datetime=datetime)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_subscription():
    form = SubscriptionForm()
    # Re-add choices population
    form.assigned_to_id.choices = [
        (user.id, user.username) for user in User.query.order_by('username').all()]
    form.assigned_to_id.choices.insert(0, (0, 'None'))
    if form.validate_on_submit():
        assigned_to_user = None
        if form.assigned_to_id.data != 0:
            assigned_to_user = User.query.get(form.assigned_to_id.data)

        subscription = Subscription(
            name=form.name.data,
            vendor=form.vendor.data,
            renewal_date=form.renewal_date.data,
            # end_date=form.end_date.data, # Keep commented if it was
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
    # Re-add choices population
    form.assigned_to_id.choices = [
        (user.id, user.username) for user in User.query.order_by('username').all()]
    form.assigned_to_id.choices.insert(0, (0, 'None'))
    if request.method == 'POST' and form.validate_on_submit():
        assigned_to_user = None
        if form.assigned_to_id.data != 0:
            assigned_to_user = User.query.get(form.assigned_to_id.data)

        subscription.name = form.name.data
        subscription.vendor = form.vendor.data
        subscription.renewal_date = form.renewal_date.data
        # subscription.end_date = form.end_date.data # Keep commented if it was
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
    return render_template(
        'subscriptions/edit.html',
        form=form,
        subscription=subscription)


@bp.route('/view/<int:id>')
@login_required
def view_subscription(id):
    subscription = Subscription.query.get_or_404(id)
    return render_template(
        'subscriptions/view.html',
        subscription=subscription)


@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_subscription(id):
    subscription = Subscription.query.get_or_404(id)
    db.session.delete(subscription)
    db.session.commit()
    flash('Subscription deleted successfully!', 'success')
    return redirect(url_for('subscriptions.list_subscriptions'))


@bp.route('/renew/<int:id>')
@login_required
def renew_subscription(id):
    subscription = Subscription.query.get_or_404(id)

    # Store the previous renewal date for logging
    previous_renewal_date = subscription.renewal_date

    # If renewal_date is None, use current date as base
    if subscription.renewal_date is None:
        base_date = datetime.utcnow().date()
    else:
        base_date = subscription.renewal_date

    # Calculate new renewal date based on frequency
    new_renewal_date = None
    if subscription.frequency == 'monthly':
        new_renewal_date = base_date + relativedelta(months=+1)
    elif subscription.frequency == 'annually':
        new_renewal_date = base_date + relativedelta(years=+1)
    elif subscription.frequency == 'quarterly':
        new_renewal_date = base_date + relativedelta(months=+3)
    else:
        flash('Cannot renew subscription: frequency not set or invalid.', 'error')
        return redirect(url_for('subscriptions.list_subscriptions'))

    # Update subscription
    subscription.renewal_date = new_renewal_date
    subscription.updated_at = datetime.utcnow()

    # Create renewal log entry
    renewal_log = SubscriptionRenewalLog(
        subscription_id=subscription.id,
        user_id=current_user.id,
        previous_renewal_date=previous_renewal_date,
        new_renewal_date=new_renewal_date,
        frequency=subscription.frequency,
        ip_address=get_client_ip(),
        notes=f"Subscription renewed from {previous_renewal_date.strftime('%Y-%m-%d') if previous_renewal_date else 'Not Set'} to {new_renewal_date.strftime('%Y-%m-%d')}"
    )

    # Save both subscription and log
    db.session.add(renewal_log)
    db.session.commit()

    flash(f'Subscription renewed successfully! Next renewal: {new_renewal_date.strftime("%Y-%m-%d")}', 'success')
    return redirect(url_for('subscriptions.list_subscriptions'))


@bp.route('/renewal-logs')
@login_required
def renewal_logs():
    page = request.args.get('page', 1, type=int)
    logs = SubscriptionRenewalLog.query.order_by(
        SubscriptionRenewalLog.renewed_at.desc()
    ).paginate(
        page=page,
        per_page=20,
        error_out=False
    )
    return render_template('subscriptions/renewal_logs.html', logs=logs)


@bp.route('/renewal-logs/<int:subscription_id>')
@login_required
def subscription_renewal_logs(subscription_id):
    subscription = Subscription.query.get_or_404(subscription_id)
    page = request.args.get('page', 1, type=int)
    logs = SubscriptionRenewalLog.query.filter_by(
        subscription_id=subscription_id
    ).order_by(
        SubscriptionRenewalLog.renewed_at.desc()
    ).paginate(
        page=page,
        per_page=10,
        error_out=False
    )
    return render_template('subscriptions/subscription_renewal_logs.html',
                         logs=logs, subscription=subscription)