from flask import render_template, redirect, url_for, flash, request, Blueprint
from flask_login import login_required, current_user
from . import bp
from .. import db
from ..models import OfficeInventory, User
from .forms import OfficeInventoryForm
from datetime import datetime

@bp.route('/')
@login_required
def list_inventory():
    inventory_items = OfficeInventory.query.all()
    return render_template('office_inventory/list.html', inventory_items=inventory_items)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_inventory_item():
    form = OfficeInventoryForm()
    form.assigned_to_id.choices = [(user.id, user.username) for user in User.query.order_by('username').all()]
    form.assigned_to_id.choices.insert(0, (0, 'None')) # Add a 'None' option

    if form.validate_on_submit():
        assigned_to_user = None
        if form.assigned_to_id.data != 0:
            assigned_to_user = User.query.get(form.assigned_to_id.data)

        item = OfficeInventory(
            item_name=form.item_name.data,
            category=form.category.data,
            quantity=form.quantity.data,
            location=form.location.data,
            purchase_date=form.purchase_date.data,
            cost=form.cost.data,
            status=form.status.data,
            notes=form.notes.data,
            assigned_to=assigned_to_user
        )
        db.session.add(item)
        db.session.commit()
        flash('Inventory item created successfully!', 'success')
        return redirect(url_for('office_inventory.list_inventory'))
    return render_template('office_inventory/create.html', form=form)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_inventory_item(id):
    item = OfficeInventory.query.get_or_404(id)
    form = OfficeInventoryForm(obj=item)
    form.assigned_to_id.choices = [(user.id, user.username) for user in User.query.order_by('username').all()]
    form.assigned_to_id.choices.insert(0, (0, 'None')) # Add a 'None' option

    if request.method == 'POST' and form.validate_on_submit():
        assigned_to_user = None
        if form.assigned_to_id.data != 0:
            assigned_to_user = User.query.get(form.assigned_to_id.data)

        item.item_name = form.item_name.data
        item.category = form.category.data
        item.quantity = form.quantity.data
        item.location = form.location.data
        item.purchase_date = form.purchase_date.data
        item.cost = form.cost.data
        item.status = form.status.data
        item.notes = form.notes.data
        item.assigned_to = assigned_to_user
        item.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Inventory item updated successfully!', 'success')
        return redirect(url_for('office_inventory.list_inventory'))
    elif request.method == 'GET':
        if item.assigned_to:
            form.assigned_to_id.data = item.assigned_to.id
        else:
            form.assigned_to_id.data = 0
    return render_template('office_inventory/edit.html', form=form, item=item)

@bp.route('/view/<int:id>')
@login_required
def view_inventory_item(id):
    item = OfficeInventory.query.get_or_404(id)
    return render_template('office_inventory/view.html', item=item)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_inventory_item(id):
    item = OfficeInventory.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Inventory item deleted successfully!', 'success')
    return redirect(url_for('office_inventory.list_inventory'))
