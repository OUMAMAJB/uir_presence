"""
Décorateurs de permissions pour le système à 5 comptes
"""

from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def super_admin_required(f):
    """Seul le Super Admin peut accéder"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Veuillez vous connecter pour accéder à cette page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if current_user.role.name != 'super_admin':
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
        
        allowed_roles = ['super_admin', 'admin_dept']
        if current_user.role.name not in allowed_roles:
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
        
        allowed_roles = ['super_admin', 'admin_dept', 'admin_filiere']
        if current_user.role.name not in allowed_roles:
            flash('Accès refusé. Vous devez être Chef de Filière.', 'danger')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    """Enseignant ou tout admin peut accéder"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Veuillez vous connecter pour accéder à cette page.', 'warning')
            return redirect(url_for('auth.login'))
        
        allowed_roles = ['super_admin', 'admin_dept', 'admin_filiere', 'enseignant']
        if current_user.role.name not in allowed_roles:
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
        
        if current_user.role.name != 'etudiant':
            flash('Accès refusé. Cette page est réservée aux étudiants.', 'danger')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def get_dashboard_for_role(role_name):
    """Retourne l'URL du dashboard approprié selon le rôle"""
    dashboards = {
        'super_admin': 'admin.dashboard',
        'admin_dept': 'department.dashboard',
        'admin_filiere': 'track.dashboard',
        'enseignant': 'teacher.dashboard',
        'etudiant': 'student.dashboard'
    }
    return dashboards.get(role_name, 'main.index')
