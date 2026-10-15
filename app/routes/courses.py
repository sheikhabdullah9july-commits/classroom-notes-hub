from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Course, Note

courses_bp = Blueprint('courses', __name__)

# All Courses List
@courses_bp.route('/')
def index():
    courses = Course.query.order_by(Course.created_at.desc()).all()
    return render_template('courses/index.html', courses=courses)

# Add New Course (Admin/Teacher only)
@courses_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    # Only admin and teacher can add courses
    if current_user.role not in ['admin', 'teacher']:
        flash('You do not have permission to add courses.', 'danger')
        return redirect(url_for('courses.index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        code = request.form.get('code')
        description = request.form.get('description')
        
        # Check if course code already exists
        if Course.query.filter_by(code=code).first():
            flash('Course code already exists!', 'danger')
            return redirect(url_for('courses.add'))
        
        # Create new course
        course = Course(name=name, code=code, description=description)
        db.session.add(course)
        db.session.commit()
        
        flash(f'Course "{name}" added successfully!', 'success')
        return redirect(url_for('courses.index'))
    
    return render_template('courses/add.html')

# View Single Course
@courses_bp.route('/<int:id>')
def view(id):
    course = Course.query.get_or_404(id)
    # Get approved notes for this course
    notes = Note.query.filter_by(course_id=id, is_approved=True).order_by(Note.uploaded_at.desc()).all()
    return render_template('courses/view.html', course=course, notes=notes)

# Edit Course (Admin/Teacher only)
@courses_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    course = Course.query.get_or_404(id)
    
    if current_user.role not in ['admin', 'teacher']:
        flash('You do not have permission to edit courses.', 'danger')
        return redirect(url_for('courses.index'))
    
    if request.method == 'POST':
        course.name = request.form.get('name')
        course.code = request.form.get('code')
        course.description = request.form.get('description')
        
        db.session.commit()
        flash('Course updated successfully!', 'success')
        return redirect(url_for('courses.view', id=id))
    
    return render_template('courses/edit.html', course=course)

# Delete Course (Admin only)
@courses_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    if current_user.role != 'admin':
        flash('Only admin can delete courses.', 'danger')
        return redirect(url_for('courses.index'))
    
    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    
    flash('Course deleted successfully!', 'success')
    return redirect(url_for('courses.index'))

