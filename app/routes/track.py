"""
Routes pour le Chef de Filière
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import Track, Subject, User, Semester, AcademicYear, Role, Session, Attendance, db, PasswordResetToken
from app.decorators import track_admin_required, teacher_required
from datetime import datetime
import pandas as pd
import secrets
from flask_mail import Message
from app import mail

track_bp = Blueprint('track', __name__)

@track_bp.route('/dashboard')
@track_admin_required
def dashboard():
    """Dashboard du Chef de Filière"""
    
    # Récupérer la filière du chef
    if current_user.role.name == 'super_admin':
        # Super admin peut voir toutes les filières
        tracks = Track.query.all()
        track = tracks[0] if tracks else None
    elif current_user.role.name == 'admin_dept':
        # Chef de département voit les filières de son département
        from app.models import Department
        department = Department.query.filter_by(head_id=current_user.id).first()
        tracks = Track.query.filter_by(department_id=department.id).all() if department else []
        track = tracks[0] if tracks else None
    else:
        # Chef de filière voit sa filière
        track = Track.query.filter_by(head_id=current_user.id).first()
        tracks = [track] if track else []
    
    if not track:
        flash('Aucune filière assignée.', 'warning')
        return render_template('track/dashboard.html', track=None, subjects=[], students=[], teachers=[])
    
    # Récupérer les données de la filière
    subjects = Subject.query.filter_by(track_id=track.id).all()
    student_role = Role.query.filter_by(name='etudiant').first()
    students = User.query.filter_by(track_id=track.id, role_id=student_role.id).all() if student_role else []
    teachers = track.teachers  # Enseignants affectés à cette filière
    
    return render_template('track/dashboard.html', 
                         track=track, 
                         tracks=tracks,
                         subjects=subjects, 
                         students=students, 
                         teachers=teachers)

# ========== GESTION DE LA STRUCTURE ACADÉMIQUE ==========

# Routes for unified dashboard navigation
@track_bp.route('/academic-structure')
@track_admin_required
def academic_structure():
    """Gestion des années et semestres (pour le dashboard unifié)"""
    
    if current_user.is_super_admin:
        tracks = Track.query.all()
        track = tracks[0] if tracks else None
    elif current_user.is_dept_head:
        from app.models import Department
        dept = Department.query.filter_by(head_id=current_user.id).first()
        tracks = Track.query.filter_by(department_id=dept.id).all() if dept else []
        track = tracks[0] if tracks else None
    else:
        track = Track.query.filter_by(head_id=current_user.id).first()
        tracks = [track] if track else []
    
    if not track:
        flash('Aucune filière assignée.', 'warning')
        return redirect(url_for('teacher.dashboard'))
    
    academic_years = AcademicYear.query.all()
    semesters = Semester.query.all()
    
    return render_template('track/academic_structure.html', 
                         track=track, 
                         tracks=tracks, 
                         academic_years=academic_years, 
                         semesters=semesters)

@track_bp.route('/subjects')
@track_admin_required
def subjects():
    """Gestion des matières (alias pour le dashboard unifié)"""
    return redirect(url_for('track.manage_subjects'))

@track_bp.route('/teaching-assignments')
@track_admin_required
def teaching_assignments():
    """Affectation des matières aux enseignants (pour le dashboard unifié)"""
    
    if current_user.is_super_admin:
        tracks = Track.query.all()
        track = tracks[0] if tracks else None
    elif current_user.is_dept_head:
        from app.models import Department
        dept = Department.query.filter_by(head_id=current_user.id).first()
        tracks = Track.query.filter_by(department_id=dept.id).all() if dept else []
        track = tracks[0] if tracks else None
    else:
        track = Track.query.filter_by(head_id=current_user.id).first()
        tracks = [track] if track else []
    
    if not track:
        flash('Aucune filière assignée.', 'warning')
        return redirect(url_for('teacher.dashboard'))
    
    subjects = Subject.query.filter_by(track_id=track.id).all()
    
    # Get teachers from the same department
    teacher_role = Role.query.filter_by(name='enseignant').first()
    admin_filiere_role = Role.query.filter_by(name='admin_filiere').first()
    
    teachers = User.query.filter(
        User.department_id == track.department_id,
        User.role_id.in_([teacher_role.id, admin_filiere_role.id])
    ).all()
    
    return render_template('track/teaching_assignments.html', 
                         track=track, 
                         tracks=tracks, 
                         subjects=subjects, 
                         teachers=teachers)

@track_bp.route('/students')
@track_admin_required
def students():
    """Liste des étudiants (alias pour le dashboard unifié)"""
    return redirect(url_for('track.view_students'))


@track_bp.route('/year/create', methods=['GET', 'POST'])
@track_admin_required
def create_academic_year():
    """Créer la structure de formation de la filière"""
    
    if request.method == 'POST':
        duration = request.form.get('duration')  # Nombre d'années (2, 3, 4, 5, 6)
        nomenclature = request.form.get('nomenclature')  # numeric, license, master, engineering
        year_name = request.form.get('year_name', '')  # Ex: "2024-2025" (optionnel)
        
        if not duration or not nomenclature:
            flash('La durée et la nomenclature sont requises.', 'danger')
            return redirect(request.url)
        
        try:
            duration = int(duration)
        except ValueError:
            flash('Durée invalide.', 'danger')
            return redirect(request.url)
        
        # Obtenir la filière du chef actuel
        track = Track.query.filter_by(head_id=current_user.id).first()
        if not track:
            flash('Aucune filière assignée.', 'warning')
            return redirect(url_for('track.dashboard'))
        
        # Créer l'année académique principale (référence)
        if not year_name:
            year_name = f"Formation {track.name}"
        
        # Vérifier si une année académique existe déjà pour cette filière
        existing_year = AcademicYear.query.filter_by(name=year_name).first()
        if not existing_year:
            academic_year = AcademicYear(name=year_name)
            db.session.add(academic_year)
            db.session.commit()
        else:
            academic_year = existing_year
        
        # Nomenclatures
        nomenclature_map = {
            'numeric': lambda i: f"{i}{'ère' if i == 1 else 'ème'} année",
            'license': lambda i: f"L{i}",
            'master': lambda i: f"M{i}",
            'engineering': lambda i: f"{i}A"
        }
        
        get_name = nomenclature_map.get(nomenclature, nomenclature_map['numeric'])
        
        # Créer les années de formation (semestres)
        created_count = 0
        for i in range(1, duration + 1):
            level_name = get_name(i)
            
            # Créer 2 semestres par année (S1 et S2 pour chaque niveau)
            for sem_num in [1, 2]:
                semester_name = f"{level_name} - S{sem_num}"
                
                # Vérifier si ce semestre existe déjà
                existing_semester = Semester.query.filter_by(
                    name=semester_name,
                    academic_year_id=academic_year.id,
                    track_id=track.id
                ).first()
                
                if not existing_semester:
                    semester = Semester(
                        name=semester_name,
                        academic_year_id=academic_year.id,
                        track_id=track.id
                    )
                    db.session.add(semester)
                    created_count += 1
        
        db.session.commit()
        
        flash(f'Structure de formation créée avec succès : {duration} année(s), {created_count} semestre(s) créés.', 'success')
        return redirect(url_for('track.dashboard'))
    
    return render_template('track/create_academic_year.html')

@track_bp.route('/year/<int:year_id>/semester/create', methods=['GET', 'POST'])
@track_admin_required
def create_semester(year_id):
    """Créer un semestre pour une année académique"""
    
    academic_year = AcademicYear.query.get_or_404(year_id)
    
    # Obtenir la filière du chef actuel
    track = Track.query.filter_by(head_id=current_user.id).first()
    if not track:
        flash('Aucune filière assignée.', 'warning')
        return redirect(url_for('track.dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')  # Ex: "S1", "S2"
        
        if not name:
            flash('Le nom du semestre est requis.', 'danger')
            return redirect(request.url)
        
        # Vérifier si le semestre existe déjà pour cette année et cette filière
        existing = Semester.query.filter_by(name=name, academic_year_id=year_id, track_id=track.id).first()
        if existing:
            flash(f'Le semestre "{name}" existe déjà pour cette année.', 'warning')
            return redirect(request.url)
        
        semester = Semester(name=name, academic_year_id=year_id, track_id=track.id)
        db.session.add(semester)
        db.session.commit()
        
        flash(f'Semestre "{name}" créé avec succès.', 'success')
        return redirect(url_for('track.dashboard'))
    
    return render_template('track/create_semester.html', academic_year=academic_year)

@track_bp.route('/subject/create', methods=['GET', 'POST'])
@track_admin_required
def create_subject():
    """Créer une matière pour la filière"""
    
    # Récupérer la filière du chef
    if current_user.role.name == 'super_admin':
        tracks = Track.query.all()
        track_id = request.args.get('track_id')
        track = Track.query.get(track_id) if track_id else (tracks[0] if tracks else None)
    elif current_user.role.name == 'admin_dept':
        from app.models import Department
        department = Department.query.filter_by(head_id=current_user.id).first()
        tracks = Track.query.filter_by(department_id=department.id).all() if department else []
        track = tracks[0] if tracks else None
    else:
        track = Track.query.filter_by(head_id=current_user.id).first()
        tracks = [track] if track else []
    
    if not track:
        flash('Aucune filière assignée.', 'warning')
        return redirect(url_for('track.dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        semester_id = request.form.get('semester_id')
        cm = int(request.form.get('total_sessions_cm', 0))
        td = int(request.form.get('total_sessions_td', 0))
        tp = int(request.form.get('total_sessions_tp', 0))
        
        if not name or not semester_id:
            flash('Le nom et le semestre sont requis.', 'danger')
            return redirect(request.url)
        
        # Calculer le total automatiquement
        total = cm + td + tp
        
        subject = Subject(
            name=name,
            track_id=track.id,
            semester_id=semester_id,
            total_sessions_cm=cm,
            total_sessions_td=td,
            total_sessions_tp=tp
        )
        db.session.add(subject)
        db.session.commit()
        
        flash(f'Matière "{name}" créée avec succès. Total: {total} séances ({cm} CM + {td} TD + {tp} TP).', 'success')
        return redirect(url_for('track.dashboard'))
    
    semesters = Semester.query.filter((Semester.track_id == track.id) | (Semester.track_id.is_(None))).all()
    return render_template('track/create_subject.html', track=track, tracks=tracks, semesters=semesters)

# ========== AFFECTATION DES ENSEIGNANTS AUX MATIÈRES ==========

@track_bp.route('/subject/<int:subject_id>/assign-teachers', methods=['GET', 'POST'])
@track_admin_required
def assign_subject_teachers(subject_id):
    """Affecter des enseignants à une matière"""
    
    subject = Subject.query.get_or_404(subject_id)
    
    # Vérifier les permissions
    if current_user.role.name not in ['super_admin', 'admin_dept']:
        track = Track.query.filter_by(head_id=current_user.id).first()
        if not track or subject.track_id != track.id:
            flash('Accès refusé.', 'danger')
            return redirect(url_for('track.dashboard'))
    
    # Récupérer les enseignants affectés à cette filière
    track_teachers = subject.track.teachers
    
    if request.method == 'POST':
        selected_ids = request.form.getlist('teacher_ids')
        
        # Retirer toutes les affectations actuelles
        subject.teachers.clear()
        
        # Ajouter les nouvelles affectations
        for teacher_id in selected_ids:
            teacher = User.query.get(teacher_id)
            if teacher and teacher in track_teachers:
                subject.teachers.append(teacher)
        
        db.session.commit()
        flash(f'Enseignants affectés à la matière "{subject.name}".', 'success')
        return redirect(url_for('track.dashboard'))
    
    return render_template('track/assign_subject_teachers.html', 
                         subject=subject, 
                         teachers=track_teachers)

# ========== GESTION DES ÉTUDIANTS ==========

@track_bp.route('/student/add', methods=['GET', 'POST'])
@track_admin_required
def add_student():
    """Ajouter un étudiant manuellement"""
    
    # Récupérer la filière du chef
    if current_user.role.name == 'super_admin':
        tracks = Track.query.all()
        track_id = request.args.get('track_id')
        track = Track.query.get(track_id) if track_id else (tracks[0] if tracks else None)
    elif current_user.role.name == 'admin_dept':
        from app.models import Department
        department = Department.query.filter_by(head_id=current_user.id).first()
        tracks = Track.query.filter_by(department_id=department.id).all() if department else []
        track = tracks[0] if tracks else None
    else:
        track = Track.query.filter_by(head_id=current_user.id).first()
        tracks = [track] if track else []
    
    if not track:
        flash('Aucune filière assignée.', 'warning')
        return redirect(url_for('track.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        academic_year = request.form.get('academic_year')  # 1, 2, 3, 4, 5...
        
        if User.query.filter_by(email=email).first():
            flash('Un utilisateur avec cet email existe déjà.', 'warning')
        else:
            student_role = Role.query.filter_by(name='etudiant').first()
            temp_password = secrets.token_urlsafe(16)
            
            student = User(
                email=email,
                password_hash='temp',
                first_name=first_name,
                last_name=last_name,
                role_id=student_role.id,
                track_id=track.id,
                academic_year=int(academic_year) if academic_year else None
            )
            student.set_password(temp_password)
            db.session.add(student)
            db.session.commit()
            
            # Envoyer l'email
            try:
                token = PasswordResetToken.create_token(student.id, expires_in_hours=72)
                reset_url = url_for('auth.set_password', token=token, _external=True)
                
                msg = Message(
                    subject="Bienvenue sur UIR Presence - Compte Étudiant",
                    recipients=[email],
                    html=f"""
                    <html>
                    <body style="font-family: Arial, sans-serif;">
                        <h2 style="color: #163A59;">Bienvenue sur UIR Presence !</h2>
                        <p>Bonjour {first_name} {last_name},</p>
                        <p>Votre compte étudiant a été créé avec succès.</p>
                        <p><strong>Filière :</strong> {track.name}</p>
                        <p><strong>Année :</strong> {academic_year}ème année</p>
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
                    </body>
                    </html>
                    """
                )
                mail.send(msg)
                flash(f'Étudiant ajouté avec succès ! Un email a été envoyé à {email}.', 'success')
            except Exception as e:
                flash(f'Étudiant créé, mais erreur lors de l\'envoi de l\'email : {str(e)}', 'warning')
            
            return redirect(url_for('track.dashboard'))
    
    return render_template('track/add_student.html', track=track, tracks=tracks)

@track_bp.route('/student/import', methods=['GET', 'POST'])
@track_admin_required
def import_students():
    """Importer des étudiants depuis un fichier Excel"""
    
    # Récupérer la filière du chef
    if current_user.role.name == 'super_admin':
        tracks = Track.query.all()
        track_id = request.args.get('track_id')
        track = Track.query.get(track_id) if track_id else (tracks[0] if tracks else None)
    elif current_user.role.name == 'admin_dept':
        from app.models import Department
        department = Department.query.filter_by(head_id=current_user.id).first()
        tracks = Track.query.filter_by(department_id=department.id).all() if department else []
        track = tracks[0] if tracks else None
    else:
        track = Track.query.filter_by(head_id=current_user.id).first()
        tracks = [track] if track else []
    
    if not track:
        flash('Aucune filière assignée.', 'warning')
        return redirect(url_for('track.dashboard'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Aucun fichier sélectionné.', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('Aucun fichier sélectionné.', 'danger')
            return redirect(request.url)
        
        if file:
            try:
                df = pd.read_excel(file)
                # Colonnes attendues: First Name, Last Name, Email, Academic Year
                
                student_role = Role.query.filter_by(name='etudiant').first()
                count = 0
                errors = []
                
                for index, row in df.iterrows():
                    try:
                        email = row['Email']
                        first_name = row['First Name']
                        last_name = row['Last Name']
                        academic_year = int(row.get('Academic Year', 1))
                        
                        if not User.query.filter_by(email=email).first():
                            user = User(
                                email=email,
                                password_hash='temp',
                                first_name=first_name,
                                last_name=last_name,
                                role_id=student_role.id,
                                track_id=track.id,
                                academic_year=academic_year
                            )
                            user.set_password(secrets.token_urlsafe(16))
                            db.session.add(user)
                            db.session.commit()
                            
                            # Créer le token pour l'email
                            token = PasswordResetToken.create_token(user.id, expires_in_hours=72)
                            # Note: Pour l'import en masse, on pourrait envoyer les emails en arrière-plan
                            
                            count += 1
                        else:
                            errors.append(f'Ligne {index + 2}: Email {email} existe déjà')
                    except Exception as e:
                        errors.append(f'Ligne {index + 2}: {str(e)}')
                
                if count > 0:
                    flash(f'{count} étudiant(s) importé(s) avec succès.', 'success')
                if errors:
                    flash(f'Erreurs: {"; ".join(errors[:5])}', 'warning')
                
            except Exception as e:
                flash(f'Erreur lors de la lecture du fichier : {str(e)}', 'danger')
            
            return redirect(url_for('track.dashboard'))
    
    return render_template('track/import_students.html', track=track, tracks=tracks)

@track_bp.route('/students')
@track_admin_required
def view_students():
    """Liste des étudiants avec filtre par année"""
    
    # Récupérer la filière du chef
    if current_user.role.name == 'super_admin':
        tracks = Track.query.all()
        track_id = request.args.get('track_id', type=int)
        track = Track.query.get(track_id) if track_id else (tracks[0] if tracks else None)
    elif current_user.role.name == 'admin_dept':
        from app.models import Department
        department = Department.query.filter_by(head_id=current_user.id).first()
        tracks = Track.query.filter_by(department_id=department.id).all() if department else []
        track = tracks[0] if tracks else None
    else:
        track = Track.query.filter_by(head_id=current_user.id).first()
        tracks = [track] if track else []
    
    if not track:
        flash('Aucune filière assignée.', 'warning')
        return render_template('track/students.html', students=[], track=None, tracks=[])
    
    # Filtre par année académique
    academic_year = request.args.get('academic_year', type=int)
    
    student_role = Role.query.filter_by(name='etudiant').first()
    query = User.query.filter_by(track_id=track.id, role_id=student_role.id)
    
    if academic_year:
        query = query.filter_by(academic_year=academic_year)
    
    students = query.all()
    
    # Récupérer les années disponibles
    available_years = db.session.query(User.academic_year).filter(
        User.track_id == track.id,
        User.role_id == student_role.id,
        User.academic_year.isnot(None)
    ).distinct().all()
    available_years = [y[0] for y in available_years]
    
    return render_template('track/students.html', 
                         students=students, 
                         track=track,
                         tracks=tracks,
                         available_years=available_years,
                         selected_year=academic_year)

# ========== STATISTIQUES FILIÈRE ==========

@track_bp.route('/statistics')
@track_admin_required
def statistics():
    """Statistiques globales de la filière"""
    
    # Récupérer la filière du chef
    if current_user.role.name == 'super_admin':
        tracks = Track.query.all()
        track_id = request.args.get('track_id', type=int)
        track = Track.query.get(track_id) if track_id else (tracks[0] if tracks else None)
    elif current_user.role.name == 'admin_dept':
        from app.models import Department
        department = Department.query.filter_by(head_id=current_user.id).first()
        tracks = Track.query.filter_by(department_id=department.id).all() if department else []
        track = tracks[0] if tracks else None
    else:
        track = Track.query.filter_by(head_id=current_user.id).first()
        tracks = [track] if track else []
    
    if not track:
        flash('Aucune filière assignée.', 'warning')
        return render_template('track/statistics.html', stats={})
    
    # Filtres
    subject_id = request.args.get('subject_id', type=int)
    academic_year = request.args.get('academic_year', type=int)
    
    # Récupérer les matières de la filière
    subjects = Subject.query.filter_by(track_id=track.id).all()
    
    # TODO: Implémenter le calcul des statistiques
    stats = {
        'track': track,
        'subjects': subjects,
        'selected_subject_id': subject_id,
        'selected_academic_year': academic_year
    }
    
    return render_template('track/statistics.html', stats=stats, tracks=tracks)

# ========== GESTION DES COURS (SESSIONS) ==========

@track_bp.route('/subjects')
@track_admin_required
def manage_subjects():
    """Gestion des matières (Vue Admin : Toutes les matières)"""
    
    # Récupérer la filière du chef
    if current_user.role.name == 'super_admin':
        tracks = Track.query.all()
        track_id = request.args.get('track_id', type=int)
        track = Track.query.get(track_id) if track_id else (tracks[0] if tracks else None)
    elif current_user.role.name == 'admin_dept':
        from app.models import Department
        department = Department.query.filter_by(head_id=current_user.id).first()
        tracks = Track.query.filter_by(department_id=department.id).all() if department else []
        track = tracks[0] if tracks else None
    else:
        track = Track.query.filter_by(head_id=current_user.id).first()
        tracks = [track] if track else []
    
    if not track:
        flash('Aucune filière assignée.', 'warning')
        return render_template('track/manage_subjects.html', subjects=[], tracks=[], semesters=[])
    
    # Récupérer tous les semestres
    semesters = Semester.query.all()
    
    # Filtres
    semester_id = request.args.get('semester_id', type=int)
    academic_year = request.args.get('academic_year', type=int)
    
    # Construire la requête des matières
    query = Subject.query.filter_by(track_id=track.id)
    
    if semester_id:
        query = query.filter_by(semester_id=semester_id)
    
    # Récupérer toutes les matières avant de filtrer par année
    all_subjects = query.all()
    
    # Filtrer par année (S1/S2 = 1ère année, S3/S4 = 2ème année, etc.)
    if academic_year:
        subjects = []
        for subject in all_subjects:
            if subject.semester:
                try:
                    sem_num = int(subject.semester.name.replace('S', ''))
                    year_num = (sem_num + 1) // 2
                    if year_num == academic_year:
                        subjects.append(subject)
                except:
                    pass
    else:
        subjects = all_subjects
    
    return render_template('track/manage_subjects.html',
                         subjects=subjects,
                         track=track,
                         tracks=tracks,
                         semesters=semesters,
                         selected_semester_id=semester_id,
                         selected_academic_year=academic_year)

@track_bp.route('/my-courses')
@track_admin_required
def my_courses():
    """Mes Cours (Vue Enseignant : Tous mes cours avec filtres)"""
    
    # 1. Récupérer TOUTES les matières enseignées par l'utilisateur
    all_subjects = current_user.teaching_subjects
    
    # 2. Extraire les options de filtres basées sur ces matières
    # Filières où il enseigne (unique)
    taught_tracks = list({s.track for s in all_subjects})
    taught_tracks.sort(key=lambda x: x.name)
    
    # Semestres (tous)
    semesters = Semester.query.all()
    
    # 3. Récupérer les filtres depuis la requête
    track_id = request.args.get('track_id', type=int)
    semester_id = request.args.get('semester_id', type=int)
    academic_year = request.args.get('academic_year', type=int)
    
    # 4. Appliquer les filtres
    filtered_subjects = []
    for subject in all_subjects:
        # Filtre Filière
        if track_id and subject.track_id != track_id:
            continue
            
        # Filtre Semestre
        if semester_id and subject.semester_id != semester_id:
            continue
            
        # Filtre Année (Basé sur le semestre : S1/S2=1, S3/S4=2, etc.)
        if academic_year:
            # On suppose que le nom du semestre est "S1", "S2", etc.
            try:
                sem_num = int(subject.semester.name.replace('S', ''))
                year_num = (sem_num + 1) // 2
                if year_num != academic_year:
                    continue
            except:
                pass # Si le format du nom de semestre n'est pas standard, on ignore ce filtre
            
        filtered_subjects.append(subject)
    
    # Pour le lien "Retour", on garde la filière principale gérée s'il y en a une
    current_managed_track = Track.query.filter_by(head_id=current_user.id).first()
    
    return render_template('track/my_courses.html', 
                         track=current_managed_track, 
                         tracks=taught_tracks,
                         subjects=filtered_subjects,
                         semesters=semesters,
                         selected_track_id=track_id,
                         selected_semester_id=semester_id,
                         selected_academic_year=academic_year)

# Route de compatibilité pour les anciens liens (redirige vers manage_subjects)
@track_bp.route('/courses')
@track_admin_required
def view_courses():
    return redirect(url_for('track.manage_subjects'))

@track_bp.route('/subject/<int:subject_id>/sessions')
@track_admin_required
def view_subject_sessions(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    # Vérifier les permissions
    if current_user.role.name not in ['super_admin', 'admin_dept']:
        track = Track.query.filter_by(head_id=current_user.id).first()
        if not track or subject.track_id != track.id:
            flash('Accès refusé.', 'danger')
            return redirect(url_for('track.dashboard'))
    
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
    
    return render_template('track/subject_sessions.html',
                         subject=subject,
                         sessions=sessions,
                         date_filter=date_filter,
                         type_filter=type_filter)

@track_bp.route('/session/create/<int:subject_id>', methods=['GET', 'POST'])
@track_admin_required
def create_session(subject_id):
    """Créer une nouvelle session"""
    subject = Subject.query.get_or_404(subject_id)
    
    # Vérifier les permissions
    if current_user.role.name not in ['super_admin', 'admin_dept']:
        track = Track.query.filter_by(head_id=current_user.id).first()
        if not track or subject.track_id != track.id:
            flash('Accès refusé.', 'danger')
            return redirect(url_for('track.dashboard'))

    if request.method == 'POST':
        session_type = request.form.get('type')
        date_str = request.form.get('date')
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        teacher_id = request.form.get('teacher_id')
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
            
            # Si aucun enseignant spécifié, utiliser l'utilisateur courant
            assigned_teacher_id = teacher_id if teacher_id else current_user.id
            
            session = Session(
                subject_id=subject_id,
                teacher_id=assigned_teacher_id,
                type=session_type,
                date=date,
                start_time=start_time,
                end_time=end_time
            )
            db.session.add(session)
            db.session.commit()
            
            flash('Session créée avec succès.', 'success')
            return redirect(url_for('track.view_subject_sessions', subject_id=subject.id))
            
        except ValueError:
            flash('Format de date ou heure invalide.', 'danger')
    
    
    print(f"DEBUG: Rendering create_session template with subject: {subject.name if subject else 'None'}")
    return render_template('track/create_session.html', subject=subject)

@track_bp.route('/session/<int:session_id>/edit', methods=['GET', 'POST'])
@track_admin_required
def edit_session(session_id):
    """Modifier une session"""
    session = Session.query.get_or_404(session_id)
    
    # Vérifier les permissions
    if current_user.role.name not in ['super_admin', 'admin_dept']:
        track = Track.query.filter_by(head_id=current_user.id).first()
        if not track or session.subject.track_id != track.id:
            flash('Accès refusé.', 'danger')
            return redirect(url_for('track.dashboard'))
    
    if request.method == 'POST':
        session_type = request.form.get('type')
        date_str = request.form.get('date')
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        teacher_id = request.form.get('teacher_id')
        
        try:
            session.type = session_type
            session.date = datetime.strptime(date_str, '%Y-%m-%d').date()
            session.start_time = datetime.strptime(start_time_str, '%H:%M').time()
            session.end_time = datetime.strptime(end_time_str, '%H:%M').time()
            if teacher_id:
                session.teacher_id = teacher_id
            
            db.session.commit()
            
            flash('Session modifiée avec succès.', 'success')
            return redirect(url_for('track.view_subject_sessions', subject_id=session.subject_id))
            
        except ValueError:
            flash('Format de date ou heure invalide.', 'danger')
    
    teachers = session.subject.teachers
    return render_template('track/edit_session.html', session=session, teachers=teachers)

@track_bp.route('/session/<int:session_id>/delete', methods=['POST'])
@track_admin_required
def delete_session(session_id):
    """Supprimer une session"""
    session = Session.query.get_or_404(session_id)
    subject_id = session.subject_id
    
    # Vérifier les permissions
    if current_user.role.name not in ['super_admin', 'admin_dept']:
        track = Track.query.filter_by(head_id=current_user.id).first()
        if not track or session.subject.track_id != track.id:
            flash('Accès refusé.', 'danger')
            return redirect(url_for('track.dashboard'))
    
    db.session.delete(session)
    db.session.commit()
    
    flash('Session supprimée avec succès.', 'success')
    return redirect(url_for('track.view_subject_sessions', subject_id=subject_id))

@track_bp.route('/session/<int:session_id>/start', methods=['POST'])
@track_admin_required
def start_session(session_id):
    """Démarrer une session (génère le QR code)"""
    session = Session.query.get_or_404(session_id)
    
    # Vérifier les permissions
    if current_user.role.name not in ['super_admin', 'admin_dept']:
        track = Track.query.filter_by(head_id=current_user.id).first()
        if not track or session.subject.track_id != track.id:
            return jsonify({'success': False, 'message': 'Accès refusé'}), 403
    
    # Générer un token unique
    session.qr_code_token = secrets.token_urlsafe(32)
    session.is_active = True
    session.started_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'success': True, 'token': session.qr_code_token})

@track_bp.route('/session/<int:session_id>/qr')
@track_admin_required
def session_qr(session_id):
    """Page d'affichage du QR code"""
    session = Session.query.get_or_404(session_id)
    
    # Vérifier les permissions
    if current_user.role.name not in ['super_admin', 'admin_dept']:
        track = Track.query.filter_by(head_id=current_user.id).first()
        if not track or session.subject.track_id != track.id:
            flash('Accès refusé.', 'danger')
            return redirect(url_for('track.dashboard'))
    
    return render_template('track/session_qr.html', session=session, subject=session.subject)

@track_bp.route('/session/<int:session_id>/refresh_token', methods=['POST'])
@track_admin_required
def refresh_token(session_id):
    """Rafraîchir le token QR"""
    session = Session.query.get_or_404(session_id)
    
    # Vérifier les permissions
    if current_user.role.name not in ['super_admin', 'admin_dept']:
        track = Track.query.filter_by(head_id=current_user.id).first()
        if not track or session.subject.track_id != track.id:
            return jsonify({'success': False}), 403
    
    # Générer un nouveau token
    session.qr_code_token = secrets.token_urlsafe(32)
    db.session.commit()
    
    return jsonify({'success': True, 'token': session.qr_code_token})

@track_bp.route('/session/<int:session_id>/stop', methods=['POST'])
@track_admin_required
def stop_session(session_id):
    """Arrêter une session"""
    session = Session.query.get_or_404(session_id)
    
    # Vérifier les permissions
    if current_user.role.name not in ['super_admin', 'admin_dept']:
        track = Track.query.filter_by(head_id=current_user.id).first()
        if not track or session.subject.track_id != track.id:
            return jsonify({'success': False}), 403
    
    session.is_active = False
    session.qr_code_token = None
    session.stopped_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'success': True})

@track_bp.route('/session/<int:session_id>/count')
@track_admin_required
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

@track_bp.route('/attendances')
@track_admin_required
def view_attendances():
    """Consulter les présences avec filtres"""
    
    # Récupérer la filière du chef
    if current_user.role.name == 'super_admin':
        tracks = Track.query.all()
        track_id = request.args.get('track_id', type=int)
        track = Track.query.get(track_id) if track_id else (tracks[0] if tracks else None)
    elif current_user.role.name == 'admin_dept':
        from app.models import Department
        department = Department.query.filter_by(head_id=current_user.id).first()
        tracks = Track.query.filter_by(department_id=department.id).all() if department else []
        track = tracks[0] if tracks else None
    else:
        track = Track.query.filter_by(head_id=current_user.id).first()
        tracks = [track] if track else []
    
    if not track:
        flash('Aucune filière assignée.', 'warning')
        return render_template('track/attendances.html', attendances=[], subjects=[])
    
    # Récupérer toutes les matières de la filière
    subjects = Subject.query.filter_by(track_id=track.id).all()
    
    # Filtres
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
    ).filter(Subject.track_id == track.id)
    
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
    
    return render_template('track/attendances.html',
                         attendances=attendances,
                         track=track,
                         tracks=tracks,
                         subjects=subjects,
                         semesters=semesters,
                         filters={
                             'academic_year': academic_year,
                             'semester_id': semester_id,
                             'subject_id': subject_id,
                             'type': session_type,
                             'date': date_filter
                         })