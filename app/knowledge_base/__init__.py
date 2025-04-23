from flask import Blueprint

bp = Blueprint('knowledge_base', __name__)

from . import views 