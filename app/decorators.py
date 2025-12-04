"""
Décorateurs de permissions pour le système de rôles dynamiques
Supporte les rôles additifs (Enseignant + Chef Dept + Chef Filière)
"""

from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def login_required_custom(f):
    """Vérifie que l'utilisateur est connecté"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Veuillez vous connecter pour accéder à cette page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def super_admin_required(f):
    """Seul le Super Admin peut accéder"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Veuillez vous connecter pour accéder à cette page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_super_admin:
            flash('Accès refusé. Vous devez être Super Administrateur.', 'danger')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def dept_admin_required(f):
    """Chef de Département ou Super Admin peuvent accéder"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Veuillez vous connecter pour accéder à cette page.', 'warning')
            return redirect(url_for('auth.login'))
        
        # Super Admin ou Chef de Département (dynamique via head_id)
        if not (current_user.is_super_admin or current_user.is_dept_head):
            flash('Accès refusé. Vous devez être Chef de Département.', 'danger')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def track_admin_required(f):
    """Chef de Filière, Chef de Département ou Super Admin peuvent accéder"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Veuillez vous connecter pour accéder à cette page.', 'warning')
            return redirect(url_for('auth.login'))
        
        # Super Admin, Chef de Département, ou Chef de Filière
        if not (current_user.is_super_admin or current_user.is_dept_head or current_user.is_track_head):
            flash('Accès refusé. Vous devez être Chef de Filière.', 'danger')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    """Enseignant ou tout admin peut accéder (socle enseignant)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Veuillez vous connecter pour accéder à cette page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_teacher:
            flash('Accès refusé. Vous devez être enseignant.', 'danger')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    """Seuls les étudiants peuvent accéder"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Veuillez vous connecter pour accéder à cette page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_student:
            flash('Accès refusé. Cette page est réservée aux étudiants.', 'danger')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def get_dashboard_for_role(user):
    """
    Retourne l'URL du dashboard approprié selon les rôles dynamiques de l'utilisateur.
    Priorise: Super Admin > Chef Dept > Chef Filière > Enseignant > Étudiant
    """
    if user.is_super_admin:
        return 'admin.dashboard'
    
    # Pour les enseignants (y compris chefs), rediriger vers le dashboard unifié
    if user.is_teacher:
        return 'teacher.dashboard'
    
    if user.is_student:
        return 'student.dashboard'
    
    return 'main.index'