from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models import Asset, User
from app.it_assets.forms import AssetForm
from app.it_assets import bp

@bp.route('/')
@login_required
def list_assets():
    page = request.args.get('page', 1, type=int)
    assets = Asset.query.paginate(page=page, per_page=10)
    return render_template('it_assets/list.html', assets=assets)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_asset():
    form = AssetForm()
    # Populate the assigned_to choices
    form.assigned_to.choices = [(0, 'None')] + [
        (user.id, user.username) for user in User.query.order_by(User.username).all()
    ]
    if form.validate_on_submit():
        asset = Asset(
            name=form.name.data,
            asset_type=form.asset_type.data,
            status=form.status.data,
            serial_number=form.serial_number.data,
            model=form.model.data,
            manufacturer=form.manufacturer.data,
            purchase_date=form.purchase_date.data,
            warranty_end=form.warranty_end.data,
            cost=form.cost.data,
            location=form.location.data,
            assigned_to_id=form.assigned_to.data if form.assigned_to.data != 0 else None,
            notes=form.notes.data
        )
        db.session.add(asset)
        db.session.commit()
        flash('Asset created successfully!', 'success')
        return redirect(url_for('it_assets.list_assets'))
    return render_template('it_assets/create.html', form=form)

@bp.route('/<int:asset_id>')
@login_required
def view_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    return render_template('it_assets/view.html', asset=asset)

@bp.route('/<int:asset_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    form = AssetForm(obj=asset)
    # Populate the assigned_to choices
    form.assigned_to.choices = [(0, 'None')] + [
        (user.id, user.username) for user in User.query.order_by(User.username).all()
    ]
    if form.validate_on_submit():
        asset.name = form.name.data
        asset.asset_type = form.asset_type.data
        asset.status = form.status.data
        asset.serial_number = form.serial_number.data
        asset.model = form.model.data
        asset.manufacturer = form.manufacturer.data
        asset.purchase_date = form.purchase_date.data
        asset.warranty_end = form.warranty_end.data
        asset.cost = form.cost.data
        asset.location = form.location.data
        asset.assigned_to_id = form.assigned_to.data if form.assigned_to.data != 0 else None
        asset.notes = form.notes.data
        db.session.commit()
        flash('Asset updated successfully!', 'success')
        return redirect(url_for('it_assets.view_asset', asset_id=asset.id))
    return render_template('it_assets/edit.html', form=form, asset=asset)

@bp.route('/<int:asset_id>/delete', methods=['POST'])
@login_required
def delete_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    db.session.delete(asset)
    db.session.commit()
    flash('Asset deleted successfully!', 'success')
    return redirect(url_for('it_assets.list_assets'))