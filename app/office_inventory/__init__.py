from flask import Blueprint

bp = Blueprint('office_inventory', __name__)

from . import views
