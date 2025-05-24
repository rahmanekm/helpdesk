from flask import Blueprint

bp = Blueprint('subscriptions', __name__)

from . import views
