from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_socketio import emit, join_room, leave_room
from app import db, socketio
from app.models import ChatRoom, Message, User, Notification

chat_bp = Blueprint('chat', __name__)

# Chat Home - List all rooms
@chat_bp.route('/')
@login_required
def index():
    rooms = ChatRoom.query.order_by(ChatRoom.created_at.desc()).all()
    return render_template('chat/index.html', rooms=rooms)

# Create new room
@chat_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_room():
    if request.method == 'POST':
        name = request.form.get('name')
        room_type = request.form.get('room_type', 'group')
        
        if name:
            room = ChatRoom(name=name, room_type=room_type)
            db.session.add(room)
            db.session.commit()
            flash(f'Chat room "{name}" created!', 'success')
            return redirect(url_for('chat.room', id=room.id))
    
    return render_template('chat/create.html')

# Chat Room
@chat_bp.route('/room/<int:id>')
@login_required
def room(id):
    room = ChatRoom.query.get_or_404(id)
    messages = Message.query.filter_by(room_id=id).order_by(Message.created_at.asc()).all()
    return render_template('chat/room.html', room=room, messages=messages)

# Delete room (admin only)
@chat_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_room(id):
    if current_user.role != 'admin':
        flash('Only admin can delete rooms!', 'danger')
        return redirect(url_for('chat.index'))
    
    room = ChatRoom.query.get_or_404(id)
    # Delete all messages in room
    Message.query.filter_by(room_id=id).delete()
    db.session.delete(room)
    db.session.commit()
    flash('Chat room deleted!', 'success')
    return redirect(url_for('chat.index'))

# ===== SocketIO Events =====

@socketio.on('join')
def on_join(data):
    if not current_user.is_authenticated:
        return False
    room = data['room']
    join_room(room)
    emit('status', {
        'msg': f'{current_user.username} has joined the chat.',
        'user': current_user.username
    }, room=room)

@socketio.on('leave')
def on_leave(data):
    if not current_user.is_authenticated:
        return False
    room = data['room']
    leave_room(room)
    emit('status', {
        'msg': f'{current_user.username} has left the chat.',
        'user': current_user.username
    }, room=room)

@socketio.on('message')
def on_message(data):
    if not current_user.is_authenticated:
        return False
    room_id = data['room']
    content = data['msg']

    if content and content.strip():
        # Save message to database
        message = Message(
            content=content.strip(),
            user_id=current_user.id,
            room_id=room_id
        )
        db.session.add(message)
        db.session.commit()

        # Get room name
        room = ChatRoom.query.get(room_id)

        # Send notification to all users (except sender)
        all_users = User.query.filter(User.id != current_user.id).all()
        for user in all_users:
            notif = Notification(
                user_id=user.id,
                message=f'New message in "{room.name}" from {current_user.username}',
                type='chat'
            )
            db.session.add(notif)
        db.session.commit()

        # Broadcast to room
        emit('message', {
            'msg': content,
            'user': current_user.username,
            'time': message.created_at.strftime('%H:%M'),
            'user_id': current_user.id
        }, room=room_id)
