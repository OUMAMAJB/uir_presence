"""
Routes pour le Chef de Département
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import Department, Track, User, Role, Subject, Session, Attendance, Semester, db
from app.decorators import dept_admin_required, teacher_required
from datetime import datetime
import secrets

department_bp = Blueprint('department', __name__)

@department_bp.route('/dashboard')
@dept_admin_required
def dashboard():
    """Dashboard du Chef de Département"""
    
    # Récupérer le département du chef
    if current_user.role.name == 'super_admin':
        # Super admin voit tous les départements
        departments = Department.query.all()
        department = departments[0] if departments else None
    else:
        # Chef de département voit son département
        department = Department.query.filter_by(head_id=current_user.id).first()
        departments = [department] if department else []
    
    if not department:
        flash('Aucun département assigné.', 'warning')
        return render_template('department/dashboard.html', department=None, tracks=[], students_by_track={})
    
    # Récupérer les filières du département
    tracks = Track.query.filter_by(department_id=department.id).all()
    
    # Récupérer les étudiants par filière
    student_role = Role.query.filter_by(name='etudiant').first()
    students_by_track = {}
    
    if student_role:
        for track in tracks:
            students = User.query.filter_by(track_id=track.id, role_id=student_role.id).all()
            students_by_track[track.id] = students
    
    # Récupérer les enseignants du département
    teacher_role = Role.query.filter_by(name='enseignant').first()
    admin_filiere_role = Role.query.filter_by(name='admin_filiere').first()
    
    teachers = []
    if department:
        teachers = User.query.filter(
            User.department_id == department.id,
            User.role_id.in_([teacher_role.id, admin_filiere_role.id])
        ).all()
    
    return render_template('department/dashboard.html', 
                         department=department,
                         departments=departments,
                         tracks=tracks, 
                         teachers=teachers,
                         students_by_track=students_by_track)

# ========== ROUTES POUR LE DASHBOARD UNIFIÉ ==========

@department_bp.route('/tracks')
@dept_admin_required
def tracks():
    """Liste des filières du département (pour le dashboard unifié)"""
    
    if current_user.is_super_admin:
        departments = Department.query.all()
        department = departments[0] if departments else None
    else:
        department = Department.query.filter_by(head_id=current_user.id).first()
    
    if not department:
        flash('Aucun département assigné.', 'warning')
        return redirect(url_for('teacher.dashboard'))
    
    tracks = Track.query.filter_by(department_id=department.id).all()
    
    return render_template('department/tracks.html', department=department, tracks=tracks)

@department_bp.route('/track-heads')
@dept_admin_required
def track_heads():
    """Gestion des chefs de filière (pour le dashboard unifié)"""
    
    if current_user.is_super_admin:
        departments = Department.query.all()
        department = departments[0] if departments else None
    else:
        department = Department.query.filter_by(head_id=current_user.id).first()
    
    if not department:
        flash('Aucun département assigné.', 'warning')
        return redirect(url_for('teacher.dashboard'))
    
    tracks = Track.query.filter_by(department_id=department.id).all()
    
    # Get all teachers for potential assignment
    teacher_role = Role.query.filter_by(name='enseignant').first()
    admin_filiere_role = Role.query.filter_by(name='admin_filiere').first()
    
    teachers = User.query.filter(
        User.department_id == department.id,
        User.role_id.in_([teacher_role.id, admin_filiere_role.id])
    ).all()
    
    return render_template('department/track_heads.html', department=department, tracks=tracks, teachers=teachers)

@department_bp.route('/assign-teachers')
@dept_admin_required
def assign_teachers():
    """Affectation des enseignants aux filières (pour le dashboard unifié)"""
    
    if current_user.is_super_admin:
        departments = Department.query.all()
        department = departments[0] if departments else None
    else:
        department = Department.query.filter_by(head_id=current_user.id).first()
    
    if not department:
        flash('Aucun département assigné.', 'warning')
        return redirect(url_for('teacher.dashboard'))
    
    tracks = Track.query.filter_by(department_id=department.id).all()
    
    teacher_role = Role.query.filter_by(name='enseignant').first()
    admin_filiere_role = Role.query.filter_by(name='admin_filiere').first()
    
    teachers = User.query.filter(
        User.department_id == department.id,
        User.role_id.in_([teacher_role.id, admin_filiere_role.id])
    ).all()
    
    return render_template('department/assign_teachers.html', department=department, tracks=tracks, teachers=teachers)

# ========== GESTION DES FILIÈRES ==========

@department_bp.route('/track/create', methods=['GET', 'POST'])
@dept_admin_required
def create_track():
    """Créer une nouvelle filière dans le département"""
    
    # Récupérer le département du chef
    if current_user.role.name == 'super_admin':
        departments = Department.query.all()
        department_id = request.args.get('department_id')
        department = Department.query.get(department_id) if department_id else None
    else:
        department = Department.query.filter_by(head_id=current_user.id).first()
        departments = [department] if department else []
    
    if not department and current_user.role.name != 'super_admin':
        flash('Aucun département assigné.', 'warning')
        return redirect(url_for('department.dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        dept_id = request.form.get('department_id') if current_user.role.name == 'super_admin' else department.id
        
        if not name:
            flash('Le nom de la filière est requis.', 'danger')
            return redirect(request.url)
        
        # Vérifier si la filière existe déjà
        existing = Track.query.filter_by(name=name, department_id=dept_id).first()
        if existing:
            flash(f'La filière "{name}" existe déjà dans ce département.', 'warning')
            return redirect(request.url)
        
        track = Track(name=name, department_id=dept_id)
        db.session.add(track)
        db.session.commit()
        
        flash(f'Filière "{name}" créée avec succès.', 'success')
        return redirect(url_for('department.dashboard'))
    
    return render_template('department/create_track.html', department=department, departments=departments)

@department_bp.route('/track/<int:track_id>/edit', methods=['GET', 'POST'])
@dept_admin_required
def edit_track(track_id):
    """Modifier une filière"""
    track = Track.query.get_or_404(track_id)
    
    # Vérifier les permissions
    if current_user.role.name != 'super_admin':
        department = Department.query.filter_by(head_id=current_user.id).first()
        if not department or track.department_id != department.id:
            flash('Accès refusé.', 'danger')
            return redirect(url_for('department.dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        
        if not name:
            flash('Le nom de la filière est requis.', 'danger')
            return redirect(request.url)
        
        # Vérifier si le nouveau nom existe déjà
        existing = Track.query.filter_by(name=name, department_id=track.department_id).filter(Track.id != track_id).first()
        if existing:
            flash(f'La filière "{name}" existe déjà dans ce département.', 'warning')
            return redirect(request.url)
        
        track.name = name
        db.session.commit()
        
        flash(f'Filière modifiée avec succès.', 'success')
        return redirect(url_for('department.dashboard'))
    
    return render_template('department/edit_track.html', track=track)

@department_bp.route('/track/<int:track_id>/delete', methods=['POST'])
@dept_admin_required
def delete_track(track_id):
    """Supprimer une filière"""
    track = Track.query.get_or_404(track_id)
    
    # Vérifier les permissions
    if current_user.role.name != 'super_admin':
        department = Department.query.filter_by(head_id=current_user.id).first()
        if not department or track.department_id != department.id:
            flash('Accès refusé.', 'danger')
            return redirect(url_for('department.dashboard'))
    
    # Vérifier s'il y a des étudiants inscrits
    student_role = Role.query.filter_by(name='etudiant').first()
    students_count = User.query.filter_by(track_id=track.id, role_id=student_role.id).count()
    
    if students_count > 0:
        flash(f'Impossible de supprimer la filière. {students_count} étudiant(s) y sont inscrits.', 'danger')
        return redirect(url_for('department.dashboard'))
    
    # Vérifier s'il y a des matières
    subjects_count = Subject.query.filter_by(track_id=track.id).count()
    if subjects_count > 0:
        flash(f'Impossible de supprimer la filière. {subjects_count} matière(s) y sont associées.', 'danger')
        return redirect(url_for('department.dashboard'))
    
    track_name = track.name
    db.session.delete(track)
    db.session.commit()
    
    flash(f'Filière "{track_name}" supprimée avec succès.', 'success')
    return redirect(url_for('department.dashboard'))

# ========== GESTION DES CHEFS DE FILIÈRE ==========

@department_bp.route('/track/<int:track_id>/assign-head', methods=['GET', 'POST'])
@dept_admin_required
def assign_track_head(track_id):
    """Nommer un chef de filière"""
    track = Track.query.get_or_404(track_id)
    
    # Vérifier les permissions
    if current_user.role.name != 'super_admin':
        department = Department.query.filter_by(head_id=current_user.id).first()
        if not department or track.department_id != department.id:
            flash('Accès refusé.', 'danger')
            return redirect(url_for('department.dashboard'))
    
    # Récupérer les enseignants du département
    teacher_role = Role.query.filter_by(name='enseignant').first()
    enseignant_role = Role.query.filter_by(name='enseignant').first()
    admin_filiere_role = Role.query.filter_by(name='admin_filiere').first()
    
    # Enseignants du même département
    teachers = User.query.filter(
        User.department_id == track.department_id,
        User.role_id.in_([teacher_role.id, enseignant_role.id, admin_filiere_role.id])
    ).all()
    
    if request.method == 'POST':
        teacher_id = request.form.get('teacher_id')
        
        if not teacher_id:
            flash('Veuillez sélectionner un enseignant.', 'warning')
            return redirect(url_for('department.dashboard'))
        
        new_head = User.query.get(teacher_id)
        
        if not new_head:
            flash('Enseignant introuvable.', 'danger')
            return redirect(url_for('department.dashboard'))
        
        # Vérifier que l'enseignant est du même département
        if new_head.department_id != track.department_id:
            flash('L\'enseignant doit appartenir au même département.', 'danger')
            return redirect(url_for('department.dashboard'))
        
        # Gérer l'ancien chef (le remettre enseignant titulaire)
        # SAUF s'il est chef de département ou super admin
        if track.head_id and track.head_id != int(teacher_id):
            old_head = User.query.get(track.head_id)
            if old_head:
                # Ne pas rétrograder si c'est un super admin ou chef de département
                if old_head.role.name not in ['super_admin', 'admin_dept']:
                    teacher_role = Role.query.filter_by(name='enseignant').first()
                    old_head.role = teacher_role
                    flash(f'{old_head.first_name} {old_head.last_name} est redevenu enseignant titulaire.', 'info')
        
        # Assigner le nouveau chef
        track_admin_role = Role.query.filter_by(name='admin_filiere').first()
        if not track_admin_role:
            flash('Rôle admin_filiere introuvable.', 'danger')
            return redirect(url_for('department.dashboard'))
        
        # Ne changer le rôle que si ce n'est pas un super admin ou chef de département
        if new_head.role.name not in ['super_admin', 'admin_dept']:
            new_head.role = track_admin_role
        
        track.head_id = new_head.id
        
        db.session.commit()
        flash(f'{new_head.first_name} {new_head.last_name} est maintenant chef de la filière {track.name}.', 'success')
        
        return redirect(url_for('department.dashboard'))
    
    return render_template('department/assign_track_head.html', track=track, teachers=teachers)

# ========== GESTION DES ENSEIGNANTS ==========

@department_bp.route('/teachers')
@dept_admin_required
def manage_teachers():
    """Page de gestion des enseignants du département"""
    # Vérifier les permissions
    if current_user.role.name == 'super_admin':
        department_id = request.args.get('department_id')
        department = Department.query.get_or_404(department_id) if department_id else None
    else:
        department = Department.query.filter_by(head_id=current_user.id).first()
    
    if not department and current_user.role.name != 'super_admin':
        flash('Aucun département assigné.', 'warning')
        return redirect(url_for('department.dashboard'))

    # Récupérer les enseignants
    teacher_role = Role.query.filter_by(name='enseignant').first()
    admin_filiere_role = Role.query.filter_by(name='admin_filiere').first()
    
    teachers = User.query.filter(
        User.department_id == department.id,
        User.role_id.in_([teacher_role.id, admin_filiere_role.id])
    ).all()
    
    return render_template('department/manage_teachers.html', teachers=teachers, department=department)

# ========== AFFECTATION DES ENSEIGNANTS AUX FILIÈRES ==========

@department_bp.route('/teacher/<int:teacher_id>/assign-tracks', methods=['GET', 'POST'])
@dept_admin_required
def assign_teacher_tracks(teacher_id):
    """Affecter un enseignant à une ou plusieurs filières"""
    teacher = User.query.get_or_404(teacher_id)
    
    # Vérifier les permissions
    if current_user.role.name != 'super_admin':
        department = Department.query.filter_by(head_id=current_user.id).first()
        if not department or teacher.department_id != department.id:
            flash('Accès refusé.', 'danger')
            return redirect(url_for('department.dashboard'))
    
    # Récupérer les filières du département
    if current_user.role.name == 'super_admin':
        tracks = Track.query.filter_by(department_id=teacher.department_id).all()
    else:
        department = Department.query.filter_by(head_id=current_user.id).first()
        tracks = Track.query.filter_by(department_id=department.id).all()
    
    if request.method == 'POST':
        track_ids = request.form.getlist('track_ids')
        
        # Retirer toutes les affectations actuelles
        teacher.tracks_taught.clear()
        
        # Ajouter les nouvelles affectations
        for track_id in track_ids:
            track = Track.query.get(track_id)
            if track:
                teacher.tracks_taught.append(track)
        
        db.session.commit()
        flash(f'Affectations mises à jour pour {teacher.first_name} {teacher.last_name}.', 'success')
        return redirect(url_for('department.dashboard'))
    
    return render_template('department/assign_teacher_tracks.html', teacher=teacher, tracks=tracks)

# ========== CONSULTATION DES ÉTUDIANTS ==========

@department_bp.route('/students')
@dept_admin_required
def view_students():
    """Consulter la liste des étudiants par filière"""
    
    # Récupérer le département du chef
    if current_user.role.name == 'super_admin':
        department_id = request.args.get('department_id', type=int)
        department = Department.query.get(department_id) if department_id else Department.query.first()
        departments = Department.query.all()
    else:
        department = Department.query.filter_by(head_id=current_user.id).first()
        departments = [department] if department else []
    
    if not department:
        flash('Aucun département assigné.', 'warning')
        return render_template('department/students.html', students=[], tracks=[], selected_track=None)
    
    # Récupérer les filières du département
    tracks = Track.query.filter_by(department_id=department.id).all()
    
    # Filtrer par filière si spécifié
    track_id = request.args.get('track_id', type=int)
    selected_track = Track.query.get(track_id) if track_id else None
    
    # Récupérer les étudiants
    student_role = Role.query.filter_by(name='etudiant').first()
    
    if track_id and selected_track:
        students = User.query.filter_by(track_id=track_id, role_id=student_role.id).all()
    else:
        # Tous les étudiants du département
        track_ids = [t.id for t in tracks]
        students = User.query.filter(User.track_id.in_(track_ids), User.role_id == student_role.id).all()
    
    return render_template('department/students.html', 
                         students=students, 
                         tracks=tracks, 
                         selected_track=selected_track,
                         department=department,
                         departments=departments)

# ========== GESTION DES COURS (Fonctionnalités Enseignant) ==========

@department_bp.route('/courses')
@dept_admin_required
def view_courses():
    """Page des cours avec filtres (filière, année, semestre)"""
    
    # Récupérer le département du chef
    if current_user.role.name == 'super_admin':
        department_id = request.args.get('department_id', type=int)
        department = Department.query.get(department_id) if department_id else Department.query.first()
    else:
        department = Department.query.filter_by(head_id=current_user.id).first()
    
    if not department:
        flash('Aucun département assigné.', 'warning')
        return render_template('department/courses.html', subjects=[], tracks=[], semesters=[])
    
    # Récupérer les filières du département
    tracks = Track.query.filter_by(department_id=department.id).all()
    
    # Récupérer tous les semestres
    semesters = Semester.query.all()
    
    # Filtres
    track_id = request.args.get('track_id', type=int)
    academic_year = request.args.get('academic_year', type=int)
    semester_id = request.args.get('semester_id', type=int)
    
    # Construire la requête des matières
    query = Subject.query
    
    if track_id:
        query = query.filter_by(track_id=track_id)
    else:
        # Toutes les matières du département
        track_ids = [t.id for t in tracks]
        query = query.filter(Subject.track_id.in_(track_ids))
    
    if semester_id:
        query = query.filter_by(semester_id=semester_id)
    
    subjects = query.all()
    
    return render_template('department/courses.html',
                         subjects=subjects,
                         tracks=tracks,
                         semesters=semesters,
                         selected_track_id=track_id,
                         selected_academic_year=academic_year,
                         selected_semester_id=semester_id,
                         department=department)

@department_bp.route('/subject/<int:subject_id>/sessions')
@dept_admin_required
def view_subject_sessions(subject_id):
    """Voir les sessions d'une matière avec filtres"""
    subject = Subject.query.get_or_404(subject_id)
    
    # Filtres
    date_filter = request.args.get('date')
    type_filter = request.args.get('type')
    
    # Construire la requête
    query = Session.query.filter_by(subject_id=subject_id)
    
    if date_filter:
        query = query.filter_by(date=datetime.strptime(date_filter, '%Y-%m-%d').date())
    
    if type_filter:
        query = query.filter_by(type=type_filter)
    
    sessions = query.order_by(Session.date.desc(), Session.start_time.desc()).all()
    
    return render_template('department/subject_sessions.html',
                         subject=subject,
                         sessions=sessions,
                         date_filter=date_filter,
                         type_filter=type_filter)

@department_bp.route('/session/create/<int:subject_id>', methods=['GET', 'POST'])
@dept_admin_required
def create_session(subject_id):
    """Créer une nouvelle session de cours"""
    subject = Subject.query.get_or_404(subject_id)
    
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
                teacher_id=current_user.id,
                type=session_type,
                date=date,
                start_time=start_time,
                end_time=end_time
            )
            db.session.add(session)
            db.session.commit()
            
            flash('Session créée avec succès.', 'success')
            return redirect(url_for('department.view_subject_sessions', subject_id=subject.id))
            
        except ValueError:
            flash('Format de date ou heure invalide.', 'danger')
    
    return render_template('department/create_session.html', subject=subject)

@department_bp.route('/session/<int:session_id>/edit', methods=['GET', 'POST'])
@dept_admin_required
def edit_session(session_id):
    """Modifier une session"""
    session = Session.query.get_or_404(session_id)
    
    if request.method == 'POST':
        session_type = request.form.get('type')
        date_str = request.form.get('date')
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        
        try:
            session.type = session_type
            session.date = datetime.strptime(date_str, '%Y-%m-%d').date()
            session.start_time = datetime.strptime(start_time_str, '%H:%M').time()
            session.end_time = datetime.strptime(end_time_str, '%H:%M').time()
            
            db.session.commit()
            
            flash('Session modifiée avec succès.', 'success')
            return redirect(url_for('department.view_subject_sessions', subject_id=session.subject_id))
            
        except ValueError:
            flash('Format de date ou heure invalide.', 'danger')
    
    return render_template('department/edit_session.html', session=session)

@department_bp.route('/session/<int:session_id>/delete', methods=['POST'])
@dept_admin_required
def delete_session(session_id):
    """Supprimer une session"""
    session = Session.query.get_or_404(session_id)
    subject_id = session.subject_id
    
    db.session.delete(session)
    db.session.commit()
    
    flash('Session supprimée avec succès.', 'success')
    return redirect(url_for('department.view_subject_sessions', subject_id=subject_id))

@department_bp.route('/session/<int:session_id>/start', methods=['POST'])
@dept_admin_required
def start_session(session_id):
    """Démarrer une session (génère le QR code)"""
    session = Session.query.get_or_404(session_id)
    
    # Générer un token unique
    session.qr_code_token = secrets.token_urlsafe(32)
    session.is_active = True
    session.started_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'success': True, 'token': session.qr_code_token})

@department_bp.route('/session/<int:session_id>/qr')
@dept_admin_required
def session_qr(session_id):
    """Page d'affichage du QR code"""
    session = Session.query.get_or_404(session_id)
    
    return render_template('department/session_qr.html', session=session)

@department_bp.route('/session/<int:session_id>/refresh_token', methods=['POST'])
@dept_admin_required
def refresh_token(session_id):
    """Rafraîchir le token QR (toutes les 15 secondes)"""
    session = Session.query.get_or_404(session_id)
    
    # Générer un nouveau token
    session.qr_code_token = secrets.token_urlsafe(32)
    db.session.commit()
    
    return jsonify({'success': True, 'token': session.qr_code_token})

@department_bp.route('/session/<int:session_id>/stop', methods=['POST'])
@dept_admin_required
def stop_session(session_id):
    """Arrêter une session"""
    session = Session.query.get_or_404(session_id)
    
    session.is_active = False
    session.qr_code_token = None
    session.stopped_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'success': True})

@department_bp.route('/session/<int:session_id>/count')
@dept_admin_required
def session_count(session_id):
    """Compter le nombre de présences en temps réel"""
    session = Session.query.get_or_404(session_id)
    
    # Compter les présences marquées comme "present"
    count = Attendance.query.filter_by(
        session_id=session_id,
        status='present'
    ).count()
    
    return jsonify({'success': True, 'count': count})

# ========== CONSULTATION DES PRÉSENCES ==========

@department_bp.route('/attendances')
@dept_admin_required
def view_attendances():
    """Consulter les présences avec filtres"""
    
    # Récupérer le département du chef
    if current_user.role.name == 'super_admin':
        department_id = request.args.get('department_id', type=int)
        department = Department.query.get(department_id) if department_id else Department.query.first()
    else:
        department = Department.query.filter_by(head_id=current_user.id).first()
    
    if not department:
        flash('Aucun département assigné.', 'warning')
        return render_template('department/attendances.html', attendances=[], tracks=[], subjects=[])
    
    # Récupérer les filières du département
    tracks = Track.query.filter_by(department_id=department.id).all()
    track_ids = [t.id for t in tracks]
    
    # Récupérer toutes les matières du département
    subjects = Subject.query.filter(Subject.track_id.in_(track_ids)).all()
    
    # Filtres
    track_id = request.args.get('track_id', type=int)
    academic_year = request.args.get('academic_year', type=int)
    semester_id = request.args.get('semester_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    session_type = request.args.get('type')
    date_filter = request.args.get('date')
    
    # Construire la requête
    query = db.session.query(Attendance, Session, Subject, User).join(
        Session, Attendance.session_id == Session.id
    ).join(
        Subject, Session.subject_id == Subject.id
    ).join(
        User, Attendance.student_id == User.id
    ).filter(Subject.track_id.in_(track_ids))
    
    if track_id:
        query = query.filter(Subject.track_id == track_id)
    
    if academic_year:
        query = query.filter(User.academic_year == academic_year)
    
    if semester_id:
        query = query.filter(Subject.semester_id == semester_id)
    
    if subject_id:
        query = query.filter(Subject.id == subject_id)
    
    if session_type:
        query = query.filter(Session.type == session_type)
    
    if date_filter:
        query = query.filter(Session.date == datetime.strptime(date_filter, '%Y-%m-%d').date())
    
    attendances = query.all()
    
    # Récupérer les semestres
    semesters = Semester.query.all()
    
    return render_template('department/attendances.html',
                         attendances=attendances,
                         tracks=tracks,
                         subjects=subjects,
                         semesters=semesters,
                         department=department,
                         filters={
                             'track_id': track_id,
                             'academic_year': academic_year,
                             'semester_id': semester_id,
                             'subject_id': subject_id,
                             'type': session_type,
                             'date': date_filter
                         })

# ========== STATISTIQUES DÉPARTEMENT ==========

@department_bp.route('/statistics')
@dept_admin_required
def statistics():
    """Statistiques globales du département avec filtres"""
    
    # Récupérer le département du chef
    if current_user.role.name == 'super_admin':
        department_id = request.args.get('department_id', type=int)
        department = Department.query.get(department_id) if department_id else Department.query.first()
        departments = Department.query.all()
    else:
        department = Department.query.filter_by(head_id=current_user.id).first()
        departments = [department] if department else []
    
    if not department:
        flash('Aucun département assigné.', 'warning')
        return render_template('department/statistics.html', stats={})
    
    # Récupérer les filières du département
    tracks = Track.query.filter_by(department_id=department.id).all()
    track_ids = [t.id for t in tracks]
    
    # Récupérer les matières du département
    subjects = Subject.query.filter(Subject.track_id.in_(track_ids)).all()
    
    # Récupérer les semestres
    semesters = Semester.query.all()
    
    # Filtres
    track_id = request.args.get('track_id', type=int)
    academic_year = request.args.get('academic_year', type=int)
    semester_id = request.args.get('semester_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    
    # Calculer les statistiques
    # TODO: Implémenter le calcul complet des statistiques
    
    stats = {
        'department': department,
        'tracks': tracks,
        'subjects': subjects,
        'semesters': semesters,
        'selected_track_id': track_id,
        'selected_academic_year': academic_year,
        'selected_semester_id': semester_id,
        'selected_subject_id': subject_id
    }
    
    return render_template('department/statistics.html', stats=stats, departments=departments)
