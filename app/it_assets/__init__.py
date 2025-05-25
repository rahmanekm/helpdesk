from flask import Blueprint

bp = Blueprint('it_assets', __name__, url_prefix='/it_assets')
from . import views
