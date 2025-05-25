from flask import Blueprint

main = Blueprint('main', __name__) # Reverted variable name
from . import views
