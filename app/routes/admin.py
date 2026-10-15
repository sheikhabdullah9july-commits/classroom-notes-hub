from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import User, Note, Course, Notification

admin_bp = Blueprint('admin', __name__)

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required!', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# Admin Dashboard
@admin_bp.route('/')
@login_required
@admin_required
def index():
    stats = {
        'users': User.query.count(),
        'courses': Course.query.count(),
        'notes': Note.query.count(),
        'pending_notes': Note.query.filter_by(is_approved=False).count()
    }
    pending_notes = Note.query.filter_by(is_approved=False).order_by(Note.uploaded_at.desc()).all()
    return render_template('admin/index.html', stats=stats, pending_notes=pending_notes)

# Approve Note
@admin_bp.route('/approve/<int:note_id>', methods=['POST'])
@login_required
@admin_required
def approve_note(note_id):
    note = Note.query.get_or_404(note_id)
    note.is_approved = True

    # Notify note author
    notif = Notification(
        user_id=note.user_id,
        message=f'Your note "{note.title}" has been approved!',
        type='approval'
    )
    db.session.add(notif)
    db.session.commit()

    flash(f'Note "{note.title}" approved!', 'success')
    return redirect(url_for('admin.index'))

# Reject (Delete) Note
@admin_bp.route('/reject/<int:note_id>', methods=['POST'])
@login_required
@admin_required
def reject_note(note_id):
    note = Note.query.get_or_404(note_id)
    title = note.title
    db.session.delete(note)
    db.session.commit()
    flash(f'Note "{title}" rejected and deleted!', 'warning')
    return redirect(url_for('admin.index'))

# Users Management
@admin_bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

# Change User Role
@admin_bp.route('/users/role/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def change_role(user_id):
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    
    if new_role in ['student', 'teacher', 'admin']:
        user.role = new_role
        db.session.commit()
        flash(f'User "{user.username}" role changed to {new_role}!', 'success')
    
    return redirect(url_for('admin.users'))

# Delete User
@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot delete yourself!', 'danger')
        return redirect(url_for('admin.users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f'User "{username}" deleted!', 'success')
    return redirect(url_for('admin.users'))

# All Notes (for moderation)
@admin_bp.route('/notes')
@login_required
@admin_required
def notes():
    all_notes = Note.query.order_by(Note.uploaded_at.desc()).all()
    return render_template('admin/notes.html', notes=all_notes)

