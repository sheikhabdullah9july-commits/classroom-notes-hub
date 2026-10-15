from flask import Blueprint, render_template, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Notification

notifications_bp = Blueprint('notifications', __name__)

# Get all notifications for current user
@notifications_bp.route('/')
@login_required
def index():
    notifications = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(Notification.created_at.desc()).all()
    return render_template('notifications/index.html', notifications=notifications)

# Mark notification as read
@notifications_bp.route('/read/<int:id>', methods=['POST'])
@login_required
def mark_read(id):
    notification = Notification.query.get_or_404(id)
    if notification.user_id == current_user.id:
        notification.is_read = True
        db.session.commit()
    return redirect(url_for('notifications.index'))

# Mark all as read
@notifications_bp.route('/read-all', methods=['POST'])
@login_required
def mark_all_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False)\
        .update({'is_read': True})
    db.session.commit()
    return redirect(url_for('notifications.index'))

# Delete notification
@notifications_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    notification = Notification.query.get_or_404(id)
    if notification.user_id == current_user.id:
        db.session.delete(notification)
        db.session.commit()
    return redirect(url_for('notifications.index'))

# Clear all notifications
@notifications_bp.route('/clear-all', methods=['POST'])
@login_required
def clear_all():
    Notification.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return redirect(url_for('notifications.index'))

# Get unread count (for AJAX)
@notifications_bp.route('/count')
@login_required
def count():
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({'count': count})

