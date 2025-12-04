from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Department, User, Role, db
from app.decorators import super_admin_required
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@super_admin_required
def dashboard():
    departments = Department.query.all()
    
    # Récupérer les enseignants par département
    teacher_role = Role.query.filter_by(name='enseignant').first()
    teachers_by_dept = {}
    
    if teacher_role:
        for dept in departments:
            teachers = User.query.filter_by(department_id=dept.id, role_id=teacher_role.id).all()
            teachers_by_dept[dept.id] = teachers
    
    return render_template('admin/dashboard.html', departments=departments, teachers_by_dept=teachers_by_dept)

@admin_bp.route('/department/new', methods=['GET', 'POST'])
@super_admin_required
def create_department():
    if request.method == 'POST':
        name = request.form.get('name')
        if Department.query.filter_by(name=name).first():
            flash('Department already exists.')
        else:
            dept = Department(name=name)
            db.session.add(dept)
            db.session.commit()
            flash('Department created successfully.')
            return redirect(url_for('admin.dashboard'))
    return render_template('admin/create_department.html')

@admin_bp.route('/department/<int:dept_id>/edit', methods=['GET', 'POST'])
@super_admin_required
def edit_department(dept_id):
    """Modifier un département"""
    department = Department.query.get_or_404(dept_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        
        # Vérifier si le nom existe déjà (sauf pour ce département)
        existing = Department.query.filter_by(name=name).filter(Department.id != dept_id).first()
        if existing:
            flash('Un département avec ce nom existe déjà.', 'warning')
            return redirect(request.url)
        
        department.name = name
        db.session.commit()
        flash(f'Département "{name}" modifié avec succès.', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/edit_department.html', department=department)

@admin_bp.route('/department/<int:dept_id>/delete', methods=['POST'])
@super_admin_required
def delete_department(dept_id):
    """Supprimer un département avec tout son contenu"""
    from app.models import Track, Subject, Session, Attendance
    from sqlalchemy import text
    
    department = Department.query.get_or_404(dept_id)
    dept_name = department.name
    
    # Retirer le chef de département d'abord
    if department.head_id:
        old_head = User.query.get(department.head_id)
        if old_head:
            teacher_role = Role.query.filter_by(name='enseignant').first()
            if teacher_role:
                old_head.role = teacher_role
        department.head_id = None
        db.session.commit()
    
    # Compter ce qui sera supprimé
    tracks = Track.query.filter_by(department_id=dept_id).all()
    track_ids = [t.id for t in tracks]
    tracks_count = len(tracks)
    
    subjects_count = 0
    sessions_count = 0
    attendances_count = 0
    
    if track_ids:
        subjects = Subject.query.filter(Subject.track_id.in_(track_ids)).all()
        subject_ids = [sub.id for sub in subjects]
        subjects_count = len(subjects)
        
        if subject_ids:
            sessions = Session.query.filter(Session.subject_id.in_(subject_ids)).all()
            session_ids = [sess.id for sess in sessions]
            sessions_count = len(sessions)
            
            if session_ids:
                attendances_count = Attendance.query.filter(Attendance.session_id.in_(session_ids)).count()
    
    # Retirer les enseignants du département (ne pas les supprimer)
    db.session.execute(text("UPDATE users SET department_id = NULL WHERE department_id = :dept_id"), {"dept_id": dept_id})
    
    # Supprimer les chefs de filière de ce département
    for track in tracks:
        if track.head_id:
            track.head_id = None
    db.session.commit()
    
    # Supprimer le département (cascade supprimera filières, matières, sessions, présences)
    db.session.execute(text("DELETE FROM departments WHERE id = :dept_id"), {"dept_id": dept_id})
    db.session.commit()
    
    flash(f'Département "{dept_name}" supprimé avec {tracks_count} filière(s), {subjects_count} matière(s), {sessions_count} session(s) et {attendances_count} présence(s).', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/department/<int:dept_id>/assign-head', methods=['POST'])
@super_admin_required
def assign_department_head(dept_id):
    department = Department.query.get_or_404(dept_id)
    teacher_id = request.form.get('teacher_id')
    
    if not teacher_id:
        flash('Veuillez sélectionner un enseignant.')
        return redirect(url_for('admin.dashboard'))
        
    new_head = User.query.get(teacher_id)
    
    if not new_head:
        flash('Enseignant introuvable.')
        return redirect(url_for('admin.dashboard'))
        
    # Vérifier que l'enseignant appartient au département
    if new_head.department_id != department.id:
        flash('L\'enseignant doit appartenir au département.')
        return redirect(url_for('admin.dashboard'))
        
    # Gérer l'ancien chef
    if department.head_id:
        old_head = User.query.get(department.head_id)
        if old_head:
            teacher_role = Role.query.filter_by(name='enseignant').first()
            old_head.role = teacher_role
            
    # Assigner le nouveau chef
    admin_dept_role = Role.query.filter_by(name='admin_dept').first()
    if not admin_dept_role:
        flash('Rôle admin_dept introuvable.')
        return redirect(url_for('admin.dashboard'))
        
    new_head.role = admin_dept_role
    department.head_id = new_head.id
    
    db.session.commit()
    flash(f'{new_head.first_name} {new_head.last_name} est maintenant chef du département {department.name}.')
    
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/teacher/add', methods=['GET', 'POST'])
@super_admin_required
def add_teacher():
    departments = Department.query.all()
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        department_id = request.form.get('department_id')
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            flash('Un utilisateur avec cet email existe déjà.')
        else:
            # Get teacher role
            teacher_role = Role.query.filter_by(name='enseignant').first()
            if not teacher_role:
                flash('Rôle enseignant introuvable. Veuillez initialiser les rôles.')
                return redirect(url_for('admin.dashboard'))

            # Create user (with temporary password)
            import secrets
            temp_password = secrets.token_urlsafe(16)
            
            user = User(
                email=email,
                password_hash='temp',  # Temporaire, sera écrasé
                first_name=first_name,
                last_name=last_name,
                role_id=teacher_role.id,
                department_id=department_id
            )
            user.set_password(temp_password)  # Hacher le mot de passe
            db.session.add(user)
            db.session.commit()
            
            # Créer un token de réinitialisation
            from app.models import PasswordResetToken
            token = PasswordResetToken.create_token(user.id, expires_in_hours=72)  # 72h pour créer le mot de passe
            
            # Envoyer l'email
            from flask_mail import Message
            from app import mail
            
            reset_url = url_for('auth.set_password', token=token, _external=True)
            
            try:
                msg = Message(
                    subject="Bienvenue sur UIR Presence - Créez votre mot de passe",
                    recipients=[email],
                    html=f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                            <h2 style="color: #163A59;">Bienvenue sur UIR Presence !</h2>
                            <p>Bonjour {first_name} {last_name},</p>
                            <p>Votre compte enseignant a été créé avec succès sur la plateforme UIR Presence.</p>
                            <p><strong>Email :</strong> {email}</p>
                            
                            <div style="background-color: #f2f2f2; padding: 15px; border-left: 4px solid #A1A621; margin: 20px 0;">
                                <p style="margin: 0;"><strong>Action requise :</strong></p>
                                <p style="margin: 5px 0 0 0;">Veuillez créer votre mot de passe en cliquant sur le lien ci-dessous :</p>
                            </div>
                            
                            <div style="text-align: center; margin: 30px 0;">
                                <a href="{reset_url}" 
                                   style="background: linear-gradient(to right, #A1A621, #D9CB04); 
                                          color: #163A59; 
                                          padding: 12px 30px; 
                                          text-decoration: none; 
                                          border-radius: 5px; 
                                          font-weight: bold;
                                          display: inline-block;">
                                    Créer mon mot de passe
                                </a>
                            </div>
                            
                            <p style="color: #666; font-size: 14px;">
                                <strong>Note :</strong> Ce lien est valide pendant 72 heures.
                            </p>
                            
                            <p style="color: #666; font-size: 14px;">
                                Si le bouton ne fonctionne pas, copiez et collez ce lien dans votre navigateur :<br>
                                <a href="{reset_url}" style="color: #A1A621;">{reset_url}</a>
                            </p>
                            
                            <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                            <p style="color: #999; font-size: 12px; text-align: center;">
                                © 2024 UIR Presence - Tous droits réservés
                            </p>
                        </div>
                    </body>
                    </html>
                    """
                )
                mail.send(msg)
                flash(f'Enseignant ajouté avec succès ! Un email a été envoyé à {email} pour créer son mot de passe.')
            except Exception as e:
                flash(f'Enseignant créé, mais erreur lors de l\'envoi de l\'email : {str(e)}')
                print(f"Erreur email : {e}")
            
            return redirect(url_for('admin.dashboard'))
            
    return render_template('admin/add_teacher.html', departments=departments)

@admin_bp.route('/track/create', methods=['GET', 'POST'])
@super_admin_required
def create_track():
    """Super Admin crée une filière en choisissant le département"""
    from app.models import Track
    
    departments = Department.query.all()
    
    if request.method == 'POST':
        name = request.form.get('name')
        department_id = request.form.get('department_id')
        
        if not name or not department_id:
            flash('Nom de filière et département sont requis.')
            return redirect(request.url)
            
        department = Department.query.get(department_id)
        if not department:
            flash('Département introuvable.')
            return redirect(request.url)
            
        # Vérifier si la filière existe déjà dans ce département
        existing = Track.query.filter_by(name=name, department_id=department_id).first()
        if existing:
            flash(f'La filière "{name}" existe déjà dans le département {department.name}.')
            return redirect(request.url)
            
        track = Track(name=name, department_id=department_id)
        db.session.add(track)
        db.session.commit()
        
        flash(f'Filière "{name}" créée avec succès dans {department.name}.')
        return redirect(url_for('admin.view_tracks'))
        
    return render_template('admin/create_track.html', departments=departments)

# ========== GESTION DES FILIÈRES ==========

@admin_bp.route('/tracks')
@super_admin_required
def view_tracks():
    """Consulter toutes les filières avec filtres"""
    from app.models import Track
    
    # Récupérer les paramètres de filtre
    department_id = request.args.get('department_id', type=int)
    
    # Construire la requête de base
    query = Track.query
    
    # Appliquer les filtres
    if department_id:
        query = query.filter_by(department_id=department_id)
    
    tracks = query.all()
    
    # Données pour les filtres
    departments = Department.query.all()
    
    # Récupérer les enseignants par département pour l'assignation des chefs de filière
    teacher_role = Role.query.filter_by(name='enseignant').first()
    admin_filiere_role = Role.query.filter_by(name='admin_filiere').first()
    
    teachers_by_dept = {}
    if teacher_role or admin_filiere_role:
        role_ids = [r.id for r in [teacher_role, admin_filiere_role] if r]
        for dept in departments:
            teachers = User.query.filter(
                User.department_id == dept.id,
                User.role_id.in_(role_ids)
            ).all()
            teachers_by_dept[dept.id] = teachers
    
    return render_template('admin/view_tracks.html', 
                         tracks=tracks,
                         departments=departments,
                         selected_dept=department_id,
                         teachers_by_dept=teachers_by_dept)

@admin_bp.route('/track/<int:track_id>/edit', methods=['GET', 'POST'])
@super_admin_required
def edit_track(track_id):
    """Modifier une filière"""
    from app.models import Track
    
    track = Track.query.get_or_404(track_id)
    departments = Department.query.all()
    
    if request.method == 'POST':
        name = request.form.get('name')
        department_id = request.form.get('department_id')
        
        if not name or not department_id:
            flash('Nom et département sont requis.', 'warning')
            return redirect(request.url)
        
        # Vérifier si le nom existe déjà dans ce département (sauf pour cette filière)
        existing = Track.query.filter_by(name=name, department_id=department_id).filter(Track.id != track_id).first()
        if existing:
            flash(f'Une filière avec ce nom existe déjà dans ce département.', 'warning')
            return redirect(request.url)
        
        track.name = name
        track.department_id = department_id
        db.session.commit()
        flash(f'Filière "{name}" modifiée avec succès.', 'success')
        return redirect(url_for('admin.view_tracks'))
    
    return render_template('admin/edit_track.html', track=track, departments=departments)

@admin_bp.route('/track/<int:track_id>/delete', methods=['POST'])
@super_admin_required
def delete_track(track_id):
    """Supprimer une filière avec tout son contenu"""
    from app.models import Track, Subject, Session, Attendance
    from sqlalchemy import text
    
    track = Track.query.get_or_404(track_id)
    track_name = track.name
    dept_name = track.department.name
    
    # Rétrograder le chef au rôle enseignant si nécessaire
    if track.head_id:
        old_head = User.query.get(track.head_id)
        if old_head:
            # Vérifier s'il est encore chef d'autres filières
            other_tracks = Track.query.filter(Track.head_id == old_head.id, Track.id != track_id).count()
            if other_tracks == 0 and old_head.role.name == 'admin_filiere':
                teacher_role = Role.query.filter_by(name='enseignant').first()
                if teacher_role:
                    old_head.role = teacher_role
        track.head_id = None
        db.session.commit()
    
    # Compter ce qui sera supprimé
    subjects = Subject.query.filter_by(track_id=track_id).all()
    subject_ids = [sub.id for sub in subjects]
    subjects_count = len(subjects)
    
    sessions_count = 0
    attendances_count = 0
    
    if subject_ids:
        sessions = Session.query.filter(Session.subject_id.in_(subject_ids)).all()
        session_ids = [sess.id for sess in sessions]
        sessions_count = len(sessions)
        
        if session_ids:
            attendances_count = Attendance.query.filter(Attendance.session_id.in_(session_ids)).count()
    
    # Compter et retirer les étudiants de la filière (ne pas les supprimer)
    student_role = Role.query.filter_by(name='etudiant').first()
    students_count = User.query.filter_by(track_id=track_id, role_id=student_role.id).count() if student_role else 0
    
    db.session.execute(text("UPDATE users SET track_id = NULL WHERE track_id = :track_id"), {"track_id": track_id})
    
    # Supprimer la filière (cascade supprimera matières, sessions, présences)
    db.session.execute(text("DELETE FROM tracks WHERE id = :track_id"), {"track_id": track_id})
    db.session.commit()
    
    flash(f'Filière "{track_name}" ({dept_name}) supprimée avec {subjects_count} matière(s), {sessions_count} session(s), {attendances_count} présence(s). {students_count} étudiant(s) ont été désinscrits.', 'success')
    return redirect(url_for('admin.view_tracks'))

@admin_bp.route('/track/<int:track_id>/assign-head', methods=['POST'])
@super_admin_required
def assign_track_head(track_id):
    """Assigner un chef de filière"""
    from app.models import Track
    
    track = Track.query.get_or_404(track_id)
    teacher_id = request.form.get('teacher_id')
    
    if not teacher_id:
        # Retirer le chef actuel
        if track.head_id:
            old_head = User.query.get(track.head_id)
            if old_head:
                # Vérifier s'il est encore chef d'autres filières
                other_tracks = Track.query.filter(Track.head_id == old_head.id, Track.id != track_id).count()
                if other_tracks == 0 and old_head.role.name == 'admin_filiere':
                    teacher_role = Role.query.filter_by(name='enseignant').first()
                    if teacher_role:
                        old_head.role = teacher_role
            track.head_id = None
            db.session.commit()
            flash(f'Chef de la filière {track.name} retiré.', 'success')
        return redirect(url_for('admin.view_tracks'))
    
    new_head = User.query.get(teacher_id)
    
    if not new_head:
        flash('Enseignant introuvable.', 'danger')
        return redirect(url_for('admin.view_tracks'))
    
    # Vérifier que l'enseignant appartient au département de la filière
    if new_head.department_id != track.department_id:
        flash('L\'enseignant doit appartenir au même département que la filière.', 'danger')
        return redirect(url_for('admin.view_tracks'))
    
    # Gérer l'ancien chef
    if track.head_id and track.head_id != new_head.id:
        old_head = User.query.get(track.head_id)
        if old_head:
            # Vérifier s'il est encore chef d'autres filières
            other_tracks = Track.query.filter(Track.head_id == old_head.id, Track.id != track_id).count()
            if other_tracks == 0 and old_head.role.name == 'admin_filiere':
                teacher_role = Role.query.filter_by(name='enseignant').first()
                if teacher_role:
                    old_head.role = teacher_role
    
    # Assigner le nouveau chef
    admin_filiere_role = Role.query.filter_by(name='admin_filiere').first()
    if not admin_filiere_role:
        flash('Rôle admin_filiere introuvable.', 'danger')
        return redirect(url_for('admin.view_tracks'))
    
    new_head.role = admin_filiere_role
    track.head_id = new_head.id
    
    db.session.commit()
    flash(f'{new_head.first_name} {new_head.last_name} est maintenant chef de la filière {track.name}.', 'success')
    
    return redirect(url_for('admin.view_tracks'))

# ========== STRUCTURE ACADÉMIQUE (ANNÉES & SEMESTRES) ==========

@admin_bp.route('/academic-structure')
@super_admin_required
def view_academic_structure():
    """Vue d'ensemble de la structure académique"""
    from app.models import AcademicYear, Semester, Track
    
    tracks = Track.query.order_by(Track.name).all()
    global_years = AcademicYear.query.filter(AcademicYear.track_id.is_(None)).order_by(AcademicYear.name.desc()).all()
    
    return render_template('admin/academic_structure.html', tracks=tracks, global_years=global_years)

@admin_bp.route('/academic-year/create', methods=['POST'])
@super_admin_required
def create_academic_year():
    from app.models import AcademicYear
    
    name = request.form.get('name')
    track_id = request.form.get('track_id')
    
    if not name:
        flash('Le nom de l\'année est requis.', 'warning')
        return redirect(url_for('admin.view_academic_structure'))
    
    # Convert track_id
    if track_id and track_id.isdigit():
        track_id = int(track_id)
    else:
        track_id = None
        
    # Check uniqueness (name + track_id)
    query = AcademicYear.query.filter_by(name=name)
    if track_id:
        query = query.filter_by(track_id=track_id)
    else:
        query = query.filter(AcademicYear.track_id.is_(None))
        
    if query.first():
        flash('Cette année académique existe déjà pour cette configuration.', 'warning')
        return redirect(url_for('admin.view_academic_structure'))
        
    year = AcademicYear(name=name, track_id=track_id)
    db.session.add(year)
    db.session.commit()
    
    flash(f'Année académique "{name}" créée avec succès.', 'success')
    return redirect(url_for('admin.view_academic_structure'))

@admin_bp.route('/academic-year/<int:year_id>/edit', methods=['POST'])
@super_admin_required
def edit_academic_year(year_id):
    from app.models import AcademicYear
    
    year = AcademicYear.query.get_or_404(year_id)
    name = request.form.get('name')
    
    if not name:
        flash('Le nom est requis.', 'warning')
        return redirect(url_for('admin.view_academic_structure'))
        
    existing = AcademicYear.query.filter_by(name=name).filter(AcademicYear.id != year_id).first()
    if existing:
        flash('Une autre année porte déjà ce nom.', 'warning')
        return redirect(url_for('admin.view_academic_structure'))
        
    year.name = name
    db.session.commit()
    
    flash('Année académique modifiée avec succès.', 'success')
    return redirect(url_for('admin.view_academic_structure'))

@admin_bp.route('/academic-year/<int:year_id>/delete', methods=['POST'])
@super_admin_required
def delete_academic_year(year_id):
    from app.models import AcademicYear, Semester, Subject, Session, Attendance
    from sqlalchemy import text
    
    year = AcademicYear.query.get_or_404(year_id)
    year_name = year.name
    
    # Compter ce qui sera supprimé pour le message de confirmation
    semesters = Semester.query.filter_by(academic_year_id=year_id).all()
    semester_ids = [s.id for s in semesters]
    
    subjects_count = 0
    sessions_count = 0
    attendances_count = 0
    
    if semester_ids:
        subjects = Subject.query.filter(Subject.semester_id.in_(semester_ids)).all()
        subject_ids = [sub.id for sub in subjects]
        subjects_count = len(subjects)
        
        if subject_ids:
            sessions = Session.query.filter(Session.subject_id.in_(subject_ids)).all()
            session_ids = [sess.id for sess in sessions]
            sessions_count = len(sessions)
            
            if session_ids:
                attendances_count = Attendance.query.filter(Attendance.session_id.in_(session_ids)).count()
    
    # Supprimer en cascade via SQL brut (la DB a les contraintes CASCADE)
    db.session.execute(text("DELETE FROM academic_years WHERE id = :year_id"), {"year_id": year_id})
    db.session.commit()
    
    flash(f'Année "{year_name}" supprimée avec {len(semesters)} semestre(s), {subjects_count} matière(s), {sessions_count} session(s) et {attendances_count} présence(s).', 'success')
    return redirect(url_for('admin.view_academic_structure'))

@admin_bp.route('/semester/create', methods=['POST'])
@super_admin_required
def create_semester():
    from app.models import Semester, AcademicYear
    
    name = request.form.get('name')
    year_id = request.form.get('year_id')
    track_id = request.form.get('track_id')
    
    if not name or not year_id:
        flash('Nom et année académique requis.', 'warning')
        return redirect(url_for('admin.view_academic_structure'))
        
    year = AcademicYear.query.get(year_id)
    if not year:
        flash('Année académique introuvable.', 'danger')
        return redirect(url_for('admin.view_academic_structure'))
    
    # Convert track_id to int or None
    if track_id and track_id.isdigit():
        track_id = int(track_id)
    else:
        track_id = None
        
    # Vérifier unicité dans l'année (et filière si spécifiée)
    query = Semester.query.filter_by(name=name, academic_year_id=year_id)
    if track_id:
        query = query.filter_by(track_id=track_id)
    else:
        query = query.filter(Semester.track_id.is_(None))
        
    if query.first():
        flash(f'Le semestre "{name}" existe déjà pour cette configuration.', 'warning')
        return redirect(url_for('admin.view_academic_structure'))
        
    semester = Semester(name=name, academic_year_id=year_id, track_id=track_id)
    db.session.add(semester)
    db.session.commit()
    
    msg = f'Semestre "{name}" ajouté à l\'année {year.name}'
    if track_id:
        from app.models import Track
        track = Track.query.get(track_id)
        msg += f' (Filière: {track.name})'
    
    flash(msg + '.', 'success')
    return redirect(url_for('admin.view_academic_structure'))

@admin_bp.route('/semester/<int:semester_id>/edit', methods=['POST'])
@super_admin_required
def edit_semester(semester_id):
    from app.models import Semester
    
    semester = Semester.query.get_or_404(semester_id)
    name = request.form.get('name')
    
    if not name:
        flash('Le nom est requis.', 'warning')
        return redirect(url_for('admin.view_academic_structure'))
        
    existing = Semester.query.filter_by(name=name, academic_year_id=semester.academic_year_id).filter(Semester.id != semester_id).first()
    if existing:
        flash('Un semestre avec ce nom existe déjà dans cette année.', 'warning')
        return redirect(url_for('admin.view_academic_structure'))
        
    semester.name = name
    db.session.commit()
    
    flash('Semestre modifié avec succès.', 'success')
    return redirect(url_for('admin.view_academic_structure'))

@admin_bp.route('/semester/<int:semester_id>/delete', methods=['POST'])
@super_admin_required
def delete_semester(semester_id):
    from app.models import Semester, Subject, Session, Attendance
    from sqlalchemy import text
    
    semester = Semester.query.get_or_404(semester_id)
    semester_name = semester.name
    year_name = semester.academic_year.name
    
    # Compter ce qui sera supprimé
    subjects = Subject.query.filter_by(semester_id=semester_id).all()
    subject_ids = [sub.id for sub in subjects]
    subjects_count = len(subjects)
    
    sessions_count = 0
    attendances_count = 0
    
    if subject_ids:
        sessions = Session.query.filter(Session.subject_id.in_(subject_ids)).all()
        session_ids = [sess.id for sess in sessions]
        sessions_count = len(sessions)
        
        if session_ids:
            attendances_count = Attendance.query.filter(Attendance.session_id.in_(session_ids)).count()
    
    # Supprimer en cascade via SQL brut
    db.session.execute(text("DELETE FROM semesters WHERE id = :semester_id"), {"semester_id": semester_id})
    db.session.commit()
    
    flash(f'Semestre "{semester_name}" ({year_name}) supprimé avec {subjects_count} matière(s), {sessions_count} session(s) et {attendances_count} présence(s).', 'success')
    return redirect(url_for('admin.view_academic_structure'))

@admin_bp.route('/subject/create', methods=['GET', 'POST'])
@super_admin_required
def create_subject():
    """Super Admin crée une matière en choisissant la filière"""
    from app.models import Track, Subject, Semester, AcademicYear
    
    departments = Department.query.all()
    tracks = Track.query.all()
    semesters = Semester.query.join(AcademicYear).order_by(AcademicYear.name.desc(), Semester.name).all()
    academic_years = AcademicYear.query.order_by(AcademicYear.name.desc()).all()
    
    if request.method == 'POST':
        name = request.form.get('name')
        track_id = request.form.get('track_id')
        semester_id = request.form.get('semester_id')
        total_sessions_cm = request.form.get('total_sessions_cm', 0)
        total_sessions_td = request.form.get('total_sessions_td', 0)
        total_sessions_tp = request.form.get('total_sessions_tp', 0)
        
        if not name or not track_id or not semester_id:
            flash('Nom, filière et semestre sont requis.')
            return redirect(request.url)
            
        track = Track.query.get(track_id)
        if not track:
            flash('Filière introuvable.')
            return redirect(request.url)
            
        subject = Subject(
            name=name,
            track_id=track_id,
            semester_id=semester_id,
            total_sessions_cm=int(total_sessions_cm) if total_sessions_cm else 0,
            total_sessions_td=int(total_sessions_td) if total_sessions_td else 0,
            total_sessions_tp=int(total_sessions_tp) if total_sessions_tp else 0
        )
        db.session.add(subject)
        db.session.commit()
        
        flash(f'Matière "{name}" créée avec succès dans la filière {track.name}.')
        return redirect(url_for('admin.view_subjects'))
        
    return render_template('admin/create_subject.html', departments=departments, tracks=tracks, semesters=semesters, academic_years=academic_years)

@admin_bp.route('/subjects')
@super_admin_required
def view_subjects():
    """Consulter toutes les matières avec filtres"""
    from app.models import Subject, Track, Semester, AcademicYear
    
    # Filtres
    track_id = request.args.get('track_id', type=int)
    semester_id = request.args.get('semester_id', type=int)
    
    query = Subject.query
    
    if track_id:
        query = query.filter_by(track_id=track_id)
    if semester_id:
        query = query.filter_by(semester_id=semester_id)
        
    subjects = query.all()
    
    # Données pour les filtres
    tracks = Track.query.all()
    semesters = Semester.query.join(AcademicYear).order_by(AcademicYear.name.desc(), Semester.name).all()
    
    return render_template('admin/view_subjects.html', 
                         subjects=subjects,
                         tracks=tracks,
                         semesters=semesters,
                         selected_track=track_id,
                         selected_semester=semester_id)

@admin_bp.route('/subject/<int:subject_id>/edit', methods=['GET', 'POST'])
@super_admin_required
def edit_subject(subject_id):
    from app.models import Subject, Track, Semester
    
    subject = Subject.query.get_or_404(subject_id)
    tracks = Track.query.all()
    semesters = Semester.query.all()
    
    if request.method == 'POST':
        subject.name = request.form.get('name')
        subject.track_id = request.form.get('track_id')
        subject.semester_id = request.form.get('semester_id')
        subject.total_sessions_cm = int(request.form.get('total_sessions_cm', 0))
        subject.total_sessions_td = int(request.form.get('total_sessions_td', 0))
        subject.total_sessions_tp = int(request.form.get('total_sessions_tp', 0))
        
        db.session.commit()
        flash(f'Matière "{subject.name}" modifiée avec succès.', 'success')
        return redirect(url_for('admin.view_subjects'))
        
    return render_template('admin/edit_subject.html', subject=subject, tracks=tracks, semesters=semesters)

@admin_bp.route('/subject/<int:subject_id>/delete', methods=['POST'])
@super_admin_required
def delete_subject(subject_id):
    from app.models import Subject
    
    subject = Subject.query.get_or_404(subject_id)
    name = subject.name
    db.session.delete(subject)
    db.session.commit()
    
    flash(f'Matière "{name}" supprimée avec succès.', 'success')
    return redirect(url_for('admin.view_subjects'))

@admin_bp.route('/subject/<int:subject_id>/assign-teachers', methods=['GET', 'POST'])
@super_admin_required
def assign_subject_teachers(subject_id):
    """Assigner des enseignants à une matière"""
    from app.models import Subject
    from sqlalchemy import text
    
    subject = Subject.query.get_or_404(subject_id)
    
    # Récupérer tous les enseignants éligibles (rôle enseignant, admin_dept, admin_filiere)
    teacher_role = Role.query.filter_by(name='enseignant').first()
    admin_dept_role = Role.query.filter_by(name='admin_dept').first()
    admin_filiere_role = Role.query.filter_by(name='admin_filiere').first()
    
    role_ids = [r.id for r in [teacher_role, admin_dept_role, admin_filiere_role] if r]
    
    # Filtrer par département de la filière si possible, sinon tous
    # Idéalement, on montre d'abord ceux du département
    department_id = subject.track.department_id
    
    teachers = User.query.filter(User.role_id.in_(role_ids)).order_by(
        (User.department_id == department_id).desc(), # Ceux du département en premier
        User.last_name
    ).all()
    
    if request.method == 'POST':
        # Récupérer les IDs des enseignants sélectionnés
        selected_teacher_ids = request.form.getlist('teacher_ids')
        selected_teacher_ids = [int(id) for id in selected_teacher_ids]
        
        # Supprimer toutes les assignations existantes
        db.session.execute(text("DELETE FROM teaching_assignments WHERE subject_id = :subject_id"), {"subject_id": subject_id})
        
        # Ajouter les nouvelles assignations
        for teacher_id in selected_teacher_ids:
            db.session.execute(
                text("INSERT INTO teaching_assignments (teacher_id, subject_id) VALUES (:teacher_id, :subject_id)"),
                {"teacher_id": teacher_id, "subject_id": subject_id}
            )
            
        db.session.commit()
        flash('Affectation des enseignants mise à jour.', 'success')
        return redirect(url_for('admin.view_subjects'))
        
    # Récupérer les enseignants déjà assignés
    assigned_teacher_ids = [t.id for t in subject.teachers]
    
    return render_template('admin/assign_subject_teachers.html', 
                         subject=subject, 
                         teachers=teachers, 
                         assigned_teacher_ids=assigned_teacher_ids)

@admin_bp.route('/students')
@super_admin_required
def view_students():
    """Super Admin consulte tous les étudiants avec filtres"""
    from app.models import Track, AcademicYear
    
    # Récupérer les paramètres de filtre
    department_id = request.args.get('department_id', type=int)
    track_id = request.args.get('track_id', type=int)
    year_id = request.args.get('year_id', type=int)
    
    # Récupérer le rôle étudiant
    student_role = Role.query.filter_by(name='etudiant').first()
    
    # Construire la requête de base
    query = User.query.filter_by(role_id=student_role.id)
    
    # Appliquer les filtres
    if department_id:
        # Filtrer par département via la filière
        track_ids = [t.id for t in Track.query.filter_by(department_id=department_id).all()]
        query = query.filter(User.track_id.in_(track_ids))
    
    if track_id:
        query = query.filter_by(track_id=track_id)
    
    # Pour l'instant, pas de filtre par année académique car pas de champ dans User
    # On pourrait ajouter un champ academic_year_id à User si nécessaire
    
    students = query.all()
    
    # Données pour les filtres
    departments = Department.query.all()
    tracks = Track.query.all()
    academic_years = AcademicYear.query.all()
    
    return render_template('admin/view_students.html', 
                         students=students,
                         departments=departments,
                         tracks=tracks,
                         academic_years=academic_years,
                         selected_dept=department_id,
                         selected_track=track_id,
                         selected_year=year_id)

# ========== GESTION DES ENSEIGNANTS ==========

@admin_bp.route('/teachers')
@super_admin_required
def view_teachers():
    """Consulter tous les enseignants avec filtres"""
    from app.models import Track
    
    # Récupérer les paramètres de filtre
    department_id = request.args.get('department_id', type=int)
    
    # Récupérer les rôles enseignants
    teacher_role = Role.query.filter_by(name='enseignant').first()
    admin_dept_role = Role.query.filter_by(name='admin_dept').first()
    admin_filiere_role = Role.query.filter_by(name='admin_filiere').first()
    
    role_ids = [r.id for r in [teacher_role, admin_dept_role, admin_filiere_role] if r]
    
    # Construire la requête de base
    query = User.query.filter(User.role_id.in_(role_ids))
    
    # Appliquer les filtres
    if department_id:
        query = query.filter_by(department_id=department_id)
    
    teachers = query.all()
    
    # Données pour les filtres
    departments = Department.query.all()
    
    return render_template('admin/view_teachers.html', 
                         teachers=teachers,
                         departments=departments,
                         selected_dept=department_id)

@admin_bp.route('/teacher/<int:teacher_id>/edit', methods=['GET', 'POST'])
@super_admin_required
def edit_teacher(teacher_id):
    """Modifier un enseignant"""
    teacher = User.query.get_or_404(teacher_id)
    departments = Department.query.all()
    
    if request.method == 'POST':
        teacher.first_name = request.form.get('first_name')
        teacher.last_name = request.form.get('last_name')
        teacher.department_id = request.form.get('department_id')
        
        db.session.commit()
        flash(f'Enseignant modifié avec succès.', 'success')
        return redirect(url_for('admin.view_teachers'))
    
    return render_template('admin/edit_teacher.html', teacher=teacher, departments=departments)

@admin_bp.route('/teacher/<int:teacher_id>/delete', methods=['POST'])
@super_admin_required
def delete_teacher(teacher_id):
    """Supprimer un enseignant"""
    from app.models import Session, Track
    from sqlalchemy import text
    
    teacher = User.query.get_or_404(teacher_id)
    
    # Vérifier si l'enseignant est chef de département
    dept = Department.query.filter_by(head_id=teacher_id).first()
    if dept:
        flash(f'Impossible de supprimer. {teacher.first_name} {teacher.last_name} est chef du département {dept.name}.', 'danger')
        return redirect(url_for('admin.view_teachers'))
    
    # Vérifier si l'enseignant est chef de filière
    track = Track.query.filter_by(head_id=teacher_id).first()
    if track:
        flash(f'Impossible de supprimer. {teacher.first_name} {teacher.last_name} est chef de la filière {track.name}.', 'danger')
        return redirect(url_for('admin.view_teachers'))
    
    # Vérifier si l'enseignant a des sessions
    sessions_count = Session.query.filter_by(teacher_id=teacher_id).count()
    if sessions_count > 0:
        flash(f'Impossible de supprimer. {sessions_count} session(s) sont associées à cet enseignant.', 'danger')
        return redirect(url_for('admin.view_teachers'))
    
    teacher_name = f'{teacher.first_name} {teacher.last_name}'
    
    # Supprimer les tokens de réinitialisation AVANT de toucher à l'utilisateur (via SQL brut)
    db.session.execute(text("DELETE FROM password_reset_tokens WHERE user_id = :user_id"), {"user_id": teacher_id})
    
    # Supprimer les assignations d'enseignement
    db.session.execute(text("DELETE FROM teaching_assignments WHERE teacher_id = :teacher_id"), {"teacher_id": teacher_id})
    
    # Supprimer les associations track_teachers
    db.session.execute(text("DELETE FROM track_teachers WHERE teacher_id = :teacher_id"), {"teacher_id": teacher_id})
    
    # Maintenant supprimer l'utilisateur
    db.session.execute(text("DELETE FROM users WHERE id = :user_id"), {"user_id": teacher_id})
    db.session.commit()
    
    flash(f'Enseignant "{teacher_name}" supprimé avec succès.', 'success')
    return redirect(url_for('admin.view_teachers'))

# ========== STATISTIQUES GLOBALES ==========

@admin_bp.route('/statistics')
@super_admin_required
def statistics():
    """Statistiques globales de l'établissement"""
    from app.models import Track, Subject, Session, Attendance
    
    # Compteurs globaux
    departments_count = Department.query.count()
    tracks_count = Track.query.count()
    subjects_count = Subject.query.count()
    
    teacher_role = Role.query.filter_by(name='enseignant').first()
    admin_dept_role = Role.query.filter_by(name='admin_dept').first()
    admin_filiere_role = Role.query.filter_by(name='admin_filiere').first()
    role_ids = [r.id for r in [teacher_role, admin_dept_role, admin_filiere_role] if r]
    teachers_count = User.query.filter(User.role_id.in_(role_ids)).count()
    
    student_role = Role.query.filter_by(name='etudiant').first()
    students_count = User.query.filter_by(role_id=student_role.id).count() if student_role else 0
    
    sessions_count = Session.query.count()
    attendances_count = Attendance.query.count()
    
    # Présences vs Absences
    present_count = Attendance.query.filter_by(status='present').count()
    absent_count = Attendance.query.filter_by(status='absent').count()
    
    # Statistiques par département
    departments = Department.query.all()
    dept_stats = []
    for dept in departments:
        tracks = Track.query.filter_by(department_id=dept.id).all()
        track_ids = [t.id for t in tracks]
        
        dept_teachers = User.query.filter(
            User.department_id == dept.id,
            User.role_id.in_(role_ids)
        ).count()
        
        dept_students = User.query.filter(
            User.track_id.in_(track_ids),
            User.role_id == student_role.id
        ).count() if student_role and track_ids else 0
        
        dept_stats.append({
            'department': dept,
            'tracks_count': len(tracks),
            'teachers_count': dept_teachers,
            'students_count': dept_students
        })
    
    stats = {
        'departments_count': departments_count,
        'tracks_count': tracks_count,
        'subjects_count': subjects_count,
        'teachers_count': teachers_count,
        'students_count': students_count,
        'sessions_count': sessions_count,
        'attendances_count': attendances_count,
        'present_count': present_count,
        'absent_count': absent_count,
        'dept_stats': dept_stats
    }
    
    return render_template('admin/statistics.html', stats=stats)
