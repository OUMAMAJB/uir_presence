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
        return redirect(url_for('admin.dashboard'))
        
    return render_template('admin/create_track.html', departments=departments)

@admin_bp.route('/subject/create', methods=['GET', 'POST'])
@super_admin_required
def create_subject():
    """Super Admin crée une matière en choisissant la filière"""
    from app.models import Track, Subject, Semester
    
    departments = Department.query.all()
    tracks = Track.query.all()
    semesters = Semester.query.all()
    
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
        return redirect(url_for('admin.dashboard'))
        
    return render_template('admin/create_subject.html', departments=departments, tracks=tracks, semesters=semesters)

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
