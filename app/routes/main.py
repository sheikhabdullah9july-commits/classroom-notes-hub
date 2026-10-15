from flask import Blueprint, render_template
from app.models import User, Course, Note

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    stats = {
        'notes': Note.query.filter_by(is_approved=True).count(),
        'users': User.query.count(),
        'courses': Course.query.count()
    }
    return render_template('main/index.html', stats=stats)
