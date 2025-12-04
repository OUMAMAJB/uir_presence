from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Rediriger vers le dashboard approprié selon le rôle
        from app.decorators import get_dashboard_for_role
        dashboard = get_dashboard_for_role(current_user)
        return redirect(url_for(dashboard))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            
            # Rediriger vers le dashboard approprié selon le rôle
            from app.decorators import get_dashboard_for_role
            dashboard = get_dashboard_for_role(user)
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for(dashboard))
        else:
            flash('Email ou mot de passe invalide', 'danger')
            
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/set-password/<token>', methods=['GET', 'POST'])
def set_password(token):
    from app.models import PasswordResetToken
    
    # Vérifier le token
    reset_token = PasswordResetToken.verify_token(token)
    
    if not reset_token:
        flash('Lien invalide ou expiré.')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or len(password) < 6:
            flash('Le mot de passe doit contenir au moins 6 caractères.')
            return render_template('auth/set_password.html', token=token)
        
        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas.')
            return render_template('auth/set_password.html', token=token)
        
        # Mettre à jour le mot de passe
        user = User.query.get(reset_token.user_id)
        user.set_password(password)
        
        # Marquer le token comme utilisé
        reset_token.used = True
        db.session.commit()
        
        flash('Mot de passe créé avec succès ! Vous pouvez maintenant vous connecter.')
        return redirect(url_for('auth.login'))
    
    # Récupérer l'utilisateur pour afficher son nom
    user = User.query.get(reset_token.user_id)
    return render_template('auth/set_password.html', token=token, user=user)

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Créer un token de réinitialisation
            from app.models import PasswordResetToken
            token = PasswordResetToken.create_token(user.id, expires_in_hours=24)
            
            # Envoyer l'email
            from flask_mail import Message
            from app import mail
            
            reset_url = url_for('auth.set_password', token=token, _external=True)
            
            try:
                msg = Message(
                    subject="UIR Presence - Réinitialisation de mot de passe",
                    recipients=[email],
                    html=f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                            <h2 style="color: #163A59;">Réinitialisation de mot de passe</h2>
                            <p>Bonjour {user.first_name} {user.last_name},</p>
                            <p>Vous avez demandé la réinitialisation de votre mot de passe.</p>
                            
                            <div style="background-color: #f2f2f2; padding: 15px; border-left: 4px solid #A1A621; margin: 20px 0;">
                                <p style="margin: 0;"><strong>Cliquez sur le lien ci-dessous pour réinitialiser :</strong></p>
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
                                    Réinitialiser mon mot de passe
                                </a>
                            </div>
                            
                            <p style="color: #666; font-size: 14px;">
                                <strong>Note :</strong> Ce lien est valide pendant 24 heures.
                            </p>
                            
                            <p style="color: #666; font-size: 14px;">
                                Si vous n'avez pas demandé cette réinitialisation, ignorez simplement cet email.
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
                flash('Un email de réinitialisation a été envoyé à votre adresse.')
            except Exception as e:
                flash('Erreur lors de l\'envoi de l\'email. Veuillez réessayer plus tard.')
                print(f"Erreur email: {e}")
        else:
            # Pour la sécurité, on affiche le même message même si l'email n'existe pas
            flash('Si cet email existe dans notre système, un lien de réinitialisation a été envoyé.')
        
        return redirect(url_for('auth.login'))
        
    return render_template('auth/forgot_password.html')
