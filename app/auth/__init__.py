from flask import Blueprint

auth = Blueprint('auth', __name__) # Reverted variable name
from . import views
