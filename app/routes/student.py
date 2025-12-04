"""
Routes pour les Étudiants
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import Subject, Session, Attendance, User, db
from app.decorators import student_required
from datetime import datetime
from sqlalchemy import and_

student_bp = Blueprint('student', __name__)

@student_bp.route('/dashboard')
@student_required
def dashboard():
    """Dashboard de l'étudiant"""
    
    # Récupérer les matières de l'étudiant
    subjects = current_user.enrolled_subjects
    
    # Calculer les statistiques pour chaque matière
    subject_stats = []
    
    for subject in subjects:
        stats = calculate_subject_stats(subject.id, current_user.id)
        subject_stats.append({
            'subject': subject,
            'stats': stats
        })
    
    return render_template('student/dashboard.html', subject_stats=subject_stats)

@student_bp.route('/scan')
@student_required
def scan_qr():
    """Interface de scan du QR code"""
    return render_template('student/scan_qr.html')

@student_bp.route('/scan/submit', methods=['POST'])
@student_required
def submit_scan():
    """Soumettre un scan de QR code"""
    
    data = request.get_json()
    token = data.get('token')
    
    print(f"DEBUG: Token reçu: {token}")
    
    if not token:
        return jsonify({'success': False, 'message': 'Token manquant'}), 400
    
    # Trouver la session active avec ce token
    session = Session.query.filter_by(qr_code_token=token, is_active=True).first()
    
    print(f"DEBUG: Session trouvée: {session}")
    if session:
        print(f"DEBUG: Session ID: {session.id}, Subject: {session.subject.name}, Active: {session.is_active}")
    
    if not session:
        # Vérifier si le token existe mais session non active
        inactive_session = Session.query.filter_by(qr_code_token=token).first()
        if inactive_session:
            print(f"DEBUG: Session existe mais n'est pas active. is_active={inactive_session.is_active}")
            return jsonify({'success': False, 'message': 'Cette session n\'est pas active. Le professeur doit d\'abord la démarrer.'}), 404
        else:
            print(f"DEBUG: Aucune session trouvée avec ce token")
            return jsonify({'success': False, 'message': 'QR code invalide ou expiré'}), 404
    
    # Vérifier que l'étudiant est inscrit à cette matière
    print(f"DEBUG: Enrolled subjects: {[s.name for s in current_user.enrolled_subjects]}")
    if session.subject not in current_user.enrolled_subjects:
        print(f"DEBUG: Étudiant pas inscrit à {session.subject.name}")
        return jsonify({'success': False, 'message': f'Vous n\'êtes pas inscrit à la matière: {session.subject.name}'}), 403
    
    # Vérifier que l'étudiant est dans la bonne filière
    if session.subject.track_id != current_user.track_id:
        print(f"DEBUG: Mauvaise filière. Session track: {session.subject.track_id}, User track: {current_user.track_id}")
        return jsonify({'success': False, 'message': 'Cette séance n\'est pas pour votre filière'}), 403
    
    # Vérifier si l'étudiant a déjà scanné pour cette session
    existing_attendance = Attendance.query.filter_by(
        session_id=session.id,
        student_id=current_user.id
    ).first()
    
    if existing_attendance:
        if existing_attendance.status == 'present':
            return jsonify({'success': False, 'message': 'Vous avez déjà marqué votre présence'}), 400
        else:
            # Mettre à jour le statut
            existing_attendance.status = 'present'
            existing_attendance.timestamp = datetime.utcnow()
    else:
        # Créer une nouvelle présence
        attendance = Attendance(
            session_id=session.id,
            student_id=current_user.id,
            status='present',
            timestamp=datetime.utcnow()
        )
        db.session.add(attendance)
    
    db.session.commit()
    
    print(f"DEBUG: Présence enregistrée pour {current_user.email}")
    
    return jsonify({
        'success': True, 
        'message': 'Présence enregistrée avec succès',
        'subject': session.subject.name,
        'type': session.type,
        'date': session.date.strftime('%d/%m/%Y')
    })


@student_bp.route('/subjects')
@student_required
def view_subjects():
    """Liste des matières de l'étudiant avec statistiques"""
    
    subjects = current_user.enrolled_subjects
    
    # Grouper par semestre
    subjects_by_semester = {}
    
    for subject in subjects:
        stats = calculate_subject_stats(subject.id, current_user.id)
        semester_name = subject.semester.name
        
        if semester_name not in subjects_by_semester:
            subjects_by_semester[semester_name] = []
            
        subjects_by_semester[semester_name].append({
            'subject': subject,
            'stats': stats
        })
    
    # Trier les semestres (optionnel, selon la logique de nommage)
    sorted_semesters = sorted(subjects_by_semester.items())
    
    return render_template('student/subjects.html', subjects_by_semester=sorted_semesters)

@student_bp.route('/subject/<int:subject_id>/history')
@student_required
def subject_history(subject_id):
    """Historique détaillé d'une matière"""
    
    subject = Subject.query.get_or_404(subject_id)
    
    # Vérifier que l'étudiant est inscrit
    if subject not in current_user.enrolled_subjects:
        flash('Accès refusé.', 'danger')
        return redirect(url_for('student.dashboard'))
    
    # Récupérer toutes les séances démarrées
    sessions = Session.query.filter(
        Session.subject_id == subject_id,
        Session.started_at.isnot(None)
    ).order_by(Session.date.desc(), Session.start_time.desc()).all()
    
    # Pour chaque séance, récupérer le statut de présence
    session_history = []
    
    for session in sessions:
        attendance = Attendance.query.filter_by(
            session_id=session.id,
            student_id=current_user.id
        ).first()
        
        status = attendance.status if attendance else 'absent'
        
        session_history.append({
            'session': session,
            'status': status,
            'timestamp': attendance.timestamp if attendance else None
        })
    
    # Calculer les statistiques
    stats = calculate_subject_stats(subject_id, current_user.id)
    
    return render_template('student/subject_history.html', 
                         subject=subject, 
                         session_history=session_history,
                         stats=stats)

# ========== FONCTIONS UTILITAIRES ==========

def calculate_subject_stats(subject_id, student_id):
    """
    Calculer les statistiques de présence pour une matière
    
    Retourne:
    - total_sessions: Nombre total de séances démarrées
    - present_count: Nombre de présences
    - absent_count: Nombre d'absences
    - remaining_sessions: Séances non encore effectuées
    - absence_percentage: Pourcentage d'absence
    - status: 'Admis' ou 'Rattrapage'
    - cm_td_absences: Absences en CM+TD
    - tp_absences: Absences en TP
    """
    
    subject = Subject.query.get(subject_id)
    
    # Récupérer toutes les séances démarrées
    started_sessions = Session.query.filter(
        Session.subject_id == subject_id,
        Session.started_at.isnot(None)
    ).all()
    
    total_sessions = len(started_sessions)
    
    # Compter les présences et absences
    present_count = 0
    absent_count = 0
    cm_td_absences = 0
    tp_absences = 0
    
    for session in started_sessions:
        attendance = Attendance.query.filter_by(
            session_id=session.id,
            student_id=student_id
        ).first()
        
        if attendance and attendance.status == 'present':
            present_count += 1
        else:
            absent_count += 1
            
            # Compter les absences par type
            if session.type in ['CM', 'TD']:
                cm_td_absences += 1
            elif session.type == 'TP':
                tp_absences += 1
    
    # Calculer le pourcentage d'absence
    absence_percentage = (absent_count / total_sessions * 100) if total_sessions > 0 else 0
    
    # Calculer les séances restantes (total planifié - démarrées)
    total_planned = subject.total_sessions_cm + subject.total_sessions_td + subject.total_sessions_tp
    remaining_sessions = total_planned - total_sessions
    
    # Déterminer le statut (Admis ou Rattrapage)
    status = 'Admis'
    
    # Règle 1: 25% d'absences en CM+TD → Rattrapage
    cm_td_total = sum(1 for s in started_sessions if s.type in ['CM', 'TD'])
    if cm_td_total > 0:
        cm_td_absence_percentage = (cm_td_absences / cm_td_total * 100)
        if cm_td_absence_percentage >= 25:
            status = 'Rattrapage'
    
    # Règle 2: 2 absences en TP → Rattrapage
    if tp_absences >= 2:
        status = 'Rattrapage'
    
    return {
        'total_sessions': total_sessions,
        'present_count': present_count,
        'absent_count': absent_count,
        'remaining_sessions': remaining_sessions,
        'absence_percentage': round(absence_percentage, 2),
        'status': status,
        'cm_td_absences': cm_td_absences,
        'tp_absences': tp_absences,
        'total_planned': total_planned
    }
