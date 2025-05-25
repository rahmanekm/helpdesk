from flask import Blueprint

tickets = Blueprint('tickets', __name__) # Reverted variable name
from . import views
