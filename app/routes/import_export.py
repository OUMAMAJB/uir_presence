from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import User, Role, Department, PasswordResetToken
import pandas as pd
import secrets
from flask_mail import Message
from app import mail

import_bp = Blueprint('import', __name__)

def admin_required(func):
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.name != 'admin':
            flash('Access denied.')
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return login_required(wrapper)

@import_bp.route('/import/teachers', methods=['GET', 'POST'])
@admin_required
def import_teachers():
    if request.method == 'POST':
        if 'file' not in request.files or request.files['file'].filename == '':
            flash('Aucun fichier sélectionné')
            return redirect(request.url)
        
        file = request.files['file']

        if not file.filename.endswith(('.xlsx', '.xls')):
            flash('Format de fichier invalide. Veuillez utiliser .xlsx ou .xls')
            return redirect(request.url)
        
        try:
            df = pd.read_excel(file)

            # Vérification colonnes
            required_columns = ['First Name', 'Last Name', 'Email', 'Department']
            if not all(col in df.columns for col in required_columns):
                flash(f'Format invalide. Colonnes requises : {", ".join(required_columns)}')
                return redirect(request.url)

            # Rôle enseignant
            teacher_role = Role.query.filter_by(name='enseignant').first()
            if not teacher_role:
                flash("Rôle 'enseignant' non trouvé. Veuillez le créer avant l'import.")
                return redirect(request.url)

            success_count = 0
            errors = []

            for index, row in df.iterrows():
                email = row['Email'].strip()
                
                # Vérifier doublon
                if User.query.filter_by(email=email).first():
                    errors.append(f"Ligne {index+2}: Email {email} existe déjà.")
                    continue
                
                # Vérifier département
                dept_name = row['Department'].strip()
                department = Department.query.filter_by(name=dept_name).first()
                if not department:
                    errors.append(f"Ligne {index+2}: Département '{dept_name}' introuvable.")
                    continue

                # Création du compte
                temp_password = secrets.token_urlsafe(12)
                user = User(
                    email=email,
                    first_name=row['First Name'].strip(),
                    last_name=row['Last Name'].strip(),
                    role_id=teacher_role.id,
                    department_id=department.id
                )
                user.set_password(temp_password)
                db.session.add(user)
                db.session.commit()  # nécessaire pour générer l'ID

                # Création du token pour définir le mot de passe
                try:
                    token = PasswordResetToken.create_token(user.id, expires_in_hours=72)
                    reset_url = url_for('auth.set_password', token=token, _external=True)

                    # Envoi email
                    msg = Message(
                        subject="Bienvenue sur UIR Presence - Créez votre mot de passe",
                        recipients=[email],
                        html=f"""
                        <p>Bonjour {user.first_name},</p>
                        <p>Votre compte a été créé. Veuillez définir votre mot de passe :</p>
                        <a href="{reset_url}">Créer mon mot de passe</a>
                        """
                    )
                    mail.send(msg)
                    success_count += 1
                except Exception as e:
                    errors.append(f"Erreur email pour {email}: {str(e)}")
            
            flash(f'Import terminé. {success_count} enseignants ajoutés.')
            for error in errors:
                flash(error, 'error')

        except Exception as e:
            flash(f'Erreur lors de la lecture du fichier : {str(e)}')
        
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/import_teachers.html')