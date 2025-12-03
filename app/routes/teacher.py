from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import Subject, Session, Attendance, User, db
from app.decorators import teacher_required
import qrcode
import io
import base64
import secrets
from datetime import datetime

teacher_bp = Blueprint('teacher', __name__)

@teacher_bp.route('/dashboard')
@teacher_required
def dashboard():
    # Get subjects taught by this teacher
    # Using the many-to-many relationship
    subjects = current_user.teaching_subjects
    
    # If super admin, show all subjects
    if current_user.role.name == 'super_admin':
        subjects = Subject.query.all()
        
    return render_template('teacher/dashboard.html', subjects=subjects)

@teacher_bp.route('/course/<int:subject_id>')
@teacher_required
def course_details(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    # Check permission
    if current_user.role.name not in ['super_admin', 'admin_dept', 'admin_filiere'] and current_user not in subject.teachers:
        flash('Access denied. You are not assigned to this subject.')
        return redirect(url_for('teacher.dashboard'))
        
    sessions = Session.query.filter_by(subject_id=subject.id).order_by(Session.date.desc(), Session.start_time.desc()).all()
    
    return render_template('teacher/course_details.html', subject=subject, sessions=sessions)

@teacher_bp.route('/session/create/<int:subject_id>', methods=['GET', 'POST'])
@teacher_required
def create_session(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    if current_user.role.name not in ['super_admin', 'admin_dept', 'admin_filiere'] and current_user not in subject.teachers:
        flash('You can only create sessions for your own subjects.')
        return redirect(url_for('teacher.dashboard'))
    
    if request.method == 'POST':
        session_type = request.form.get('type')
        date_str = request.form.get('date')
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
            
            session = Session(
                subject_id=subject_id,
                teacher_id=current_user.id,  # Enregistrer qui a créé la séance
                type=session_type,
                date=date,
                start_time=start_time,
                end_time=end_time
            )
            db.session.add(session)
            db.session.commit()
            
            flash('Session created successfully.')
            return redirect(url_for('teacher.course_details', subject_id=subject.id))
            
        except ValueError:
            flash('Invalid date or time format.')
    
    return render_template('teacher/create_session.html', subject=subject)

@teacher_bp.route('/session/<int:session_id>/qr')
@teacher_required
def qr_code(session_id):
    session = Session.query.get_or_404(session_id)
    
    if current_user.role.name not in ['super_admin', 'admin_dept', 'admin_filiere'] and current_user not in session.subject.teachers:
        flash('Access denied.')
        return redirect(url_for('teacher.dashboard'))
    
    return render_template('teacher/qr_code.html', session=session)

@teacher_bp.route('/session/<int:session_id>/start', methods=['POST'])
@teacher_required
def start_session(session_id):
    session = Session.query.get_or_404(session_id)
    
    if current_user.role.name not in ['super_admin', 'admin_dept', 'admin_filiere'] and current_user not in session.subject.teachers:
        return jsonify({'error': 'Access denied'}), 403
    
    # Generate a unique token for this session
    session.qr_code_token = secrets.token_urlsafe(32)
    session.is_active = True
    session.started_at = datetime.utcnow()  # Enregistrer quand la séance a été démarrée
    db.session.commit()
    
    return jsonify({'success': True, 'token': session.qr_code_token})

@teacher_bp.route('/session/<int:session_id>/refresh_token', methods=['POST'])
@teacher_required
def refresh_token(session_id):
    session = Session.query.get_or_404(session_id)
    
    if current_user.role.name not in ['super_admin', 'admin_dept', 'admin_filiere'] and current_user not in session.subject.teachers:
        return jsonify({'error': 'Access denied'}), 403
    
    # Generate a new token (refreshed every 15 seconds)
    session.qr_code_token = secrets.token_urlsafe(32)
    db.session.commit()
    
    return jsonify({'success': True, 'token': session.qr_code_token})

@teacher_bp.route('/session/<int:session_id>/stop', methods=['POST'])
@teacher_required
def stop_session(session_id):
    session = Session.query.get_or_404(session_id)
    
    if current_user.role.name not in ['super_admin', 'admin_dept', 'admin_filiere'] and current_user not in session.subject.teachers:
        return jsonify({'error': 'Access denied'}), 403
    
    session.is_active = False
    session.qr_code_token = None
    session.stopped_at = datetime.utcnow()  # Enregistrer quand la séance a été arrêtée
    db.session.commit()
    
    return jsonify({'success': True})

@teacher_bp.route('/session/<int:session_id>/attendance')
@teacher_required
def session_attendance(session_id):
    """Voir l'historique des présences pour une séance"""
    session = Session.query.get_or_404(session_id)
    
    if current_user.role.name not in ['super_admin', 'admin_dept', 'admin_filiere'] and current_user not in session.subject.teachers:
        flash('Access denied.')
        return redirect(url_for('teacher.dashboard'))
    
    # Récupérer tous les étudiants inscrits à cette matière
    students = session.subject.students
    
    # Récupérer les présences
    attendances = {}
    for attendance in session.attendances:
        attendances[attendance.student_id] = attendance
    
    # Créer la liste avec statut pour chaque étudiant
    attendance_list = []
    for student in students:
        attendance = attendances.get(student.id)
        attendance_list.append({
            'student': student,
            'status': attendance.status if attendance else 'absent',
            'timestamp': attendance.timestamp if attendance else None
        })
    
    return render_template('teacher/session_attendance.html', session=session, attendance_list=attendance_list)
