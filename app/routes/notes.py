import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Note, NoteVersion, Course, Like, Comment, Notification

notes_bp = Blueprint('notes', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Upload Note
@notes_bp.route('/upload/<int:course_id>', methods=['GET', 'POST'])
@login_required
def upload(course_id):
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        file = request.files.get('file')
        
        if not file or file.filename == '':
            flash('Please select a file!', 'danger')
            return redirect(request.url)
        
        if not allowed_file(file.filename):
            flash('File type not allowed! Use: PDF, DOC, DOCX, PPT, PPTX, TXT, PNG, JPG', 'danger')
            return redirect(request.url)
        
        # Secure filename
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        
        # Create unique filename
        unique_filename = f"{current_user.id}_{course_id}_{uuid.uuid4().hex}_{filename}"
        
        # Save file
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # Create note record
        note = Note(
            title=title,
            description=description,
            filename=unique_filename,
            file_type=file_ext,
            version=1,
            is_approved=False,  # Needs admin approval
            user_id=current_user.id,
            course_id=course_id
        )
        db.session.add(note)
        db.session.commit()
        
        flash('Note uploaded successfully! Waiting for admin approval.', 'success')
        return redirect(url_for('courses.view', id=course_id))
    
    return render_template('notes/upload.html', course=course)

def _require_visible(note):
    if not note.is_approved and not (current_user.is_authenticated and
            (current_user.id == note.user_id or current_user.role == 'admin')):
        abort(404)

# View Note
@notes_bp.route('/<int:id>')
def view(id):
    note = Note.query.get_or_404(id)
    _require_visible(note)
    # Check if current user has liked this note
    user_liked = False
    if current_user.is_authenticated:
        user_liked = Like.query.filter_by(user_id=current_user.id, note_id=id).first() is not None
    # Get comments ordered by newest first
    comments = Comment.query.filter_by(note_id=id).order_by(Comment.created_at.desc()).all()
    return render_template('notes/view.html', note=note, user_liked=user_liked, comments=comments)

# Like/Unlike Note
@notes_bp.route('/like/<int:id>', methods=['POST'])
@login_required
def like(id):
    note = Note.query.get_or_404(id)
    _require_visible(note)
    existing_like = Like.query.filter_by(user_id=current_user.id, note_id=id).first()

    if existing_like:
        # Unlike
        db.session.delete(existing_like)
        db.session.commit()
        flash('Like removed!', 'info')
    else:
        # Like
        new_like = Like(user_id=current_user.id, note_id=id)
        db.session.add(new_like)
        db.session.commit()

        # Notify note author (if not liking own note)
        if note.user_id != current_user.id:
            notif = Notification(
                user_id=note.user_id,
                message=f'{current_user.username} liked your note "{note.title}"',
                type='like'
            )
            db.session.add(notif)
            db.session.commit()

        flash('Note liked!', 'success')

    return redirect(url_for('notes.view', id=id))

# Add Comment
@notes_bp.route('/comment/<int:id>', methods=['POST'])
@login_required
def add_comment(id):
    note = Note.query.get_or_404(id)
    _require_visible(note)
    content = request.form.get('content')

    if content and content.strip():
        comment = Comment(content=content.strip(), user_id=current_user.id, note_id=id)
        db.session.add(comment)

        # Notify note author (if not commenting on own note)
        if note.user_id != current_user.id:
            notif = Notification(
                user_id=note.user_id,
                message=f'{current_user.username} commented on your note "{note.title}"',
                type='comment'
            )
            db.session.add(notif)
        db.session.commit()
        flash('Comment added!', 'success')

    return redirect(url_for('notes.view', id=id))

# Delete Comment
@notes_bp.route('/comment/delete/<int:id>', methods=['POST'])
@login_required
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    note_id = comment.note_id

    # Only comment owner or admin can delete
    if comment.user_id != current_user.id and current_user.role != 'admin':
        flash('Cannot delete this comment!', 'danger')
        return redirect(url_for('notes.view', id=note_id))

    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted!', 'success')
    return redirect(url_for('notes.view', id=note_id))

# Download Note
@notes_bp.route('/download/<int:id>')
def download(id):
    note = Note.query.get_or_404(id)
    _require_visible(note)
    upload_folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(upload_folder, note.filename, as_attachment=True)

# My Notes (User's uploaded notes)
@notes_bp.route('/my-notes')
@login_required
def my_notes():
    notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.uploaded_at.desc()).all()
    return render_template('notes/my_notes.html', notes=notes)

# All Notes (for browsing)
@notes_bp.route('/')
def index():
    notes = Note.query.filter_by(is_approved=True).order_by(Note.uploaded_at.desc()).all()
    return render_template('notes/index.html', notes=notes)

# Delete Note
@notes_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    note = Note.query.get_or_404(id)
    _require_visible(note)
    
    # Only owner or admin can delete
    if note.user_id != current_user.id and current_user.role != 'admin':
        flash('You cannot delete this note!', 'danger')
        return redirect(url_for('notes.view', id=id))
    
    # Delete file
    try:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], note.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    except:
        pass
    
    course_id = note.course_id
    db.session.delete(note)
    db.session.commit()
    
    flash('Note deleted successfully!', 'success')
    return redirect(url_for('courses.view', id=course_id))

