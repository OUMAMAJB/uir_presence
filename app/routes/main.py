from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    if current_user.role.name == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif current_user.role.name == 'admin_dept':
        return redirect(url_for('department.dashboard'))
    elif current_user.role.name == 'admin_filiere':
        return redirect(url_for('track.dashboard'))
    elif current_user.role.name == 'enseignant':
        return redirect(url_for('teacher.dashboard'))
    elif current_user.role.name == 'etudiant':
        return redirect(url_for('student.dashboard'))
    return "Unknown Role"
