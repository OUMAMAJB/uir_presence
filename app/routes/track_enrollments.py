
# ========== GESTION DES INSCRIPTIONS ==========

@track_bp.route('/subject/<int:subject_id>/enroll_students', methods=['POST'])
@track_admin_required
def enroll_students_to_subject(subject_id):
    """Inscrire tous les étudiants de la filière à une matière"""
    subject = Subject.query.get_or_404(subject_id)
    
    # Vérifier les permissions
    if current_user.role.name not in ['super_admin', 'admin_dept']:
        track = Track.query.filter_by(head_id=current_user.id).first()
        if not track or subject.track_id != track.id:
            flash('Accès refusé.', 'danger')
            return redirect(url_for('track.dashboard'))
    
    # Récupérer tous les étudiants de la filière
    students = User.query.filter_by(track_id=subject.track_id, role_id=Role.query.filter_by(name='etudiant').first().id).all()
    
    enrolled_count = 0
    for student in students:
        if subject not in student.enrolled_subjects:
            student.enrolled_subjects.append(subject)
            enrolled_count += 1
    
    db.session.commit()
    
    flash(f'{enrolled_count} étudiant(s) inscrit(s) à {subject.name}.', 'success')
    return redirect(url_for('track.manage_subjects'))

@track_bp.route('/enroll_all_students', methods=['POST'])
@track_admin_required
def enroll_all_students():
    """Inscrire tous les étudiants de la filière à toutes les matières de la filière"""
    
    # Récupérer la filière du chef
    if current_user.role.name == 'super_admin':
        track_id = request.form.get('track_id', type=int)
        track = Track.query.get(track_id) if track_id else None
    elif current_user.role.name == 'admin_dept':
        from app.models import Department
        department = Department.query.filter_by(head_id=current_user.id).first()
        track_id = request.form.get('track_id', type=int)
        track = Track.query.get(track_id) if track_id and department else None
    else:
        track = Track.query.filter_by(head_id=current_user.id).first()
    
    if not track:
        flash('Filière introuvable.', 'danger')
        return redirect(url_for('track.dashboard'))
    
    # Récupérer toutes les matières de la filière
    subjects = Subject.query.filter_by(track_id=track.id).all()
    
    # Récupérer tous les étudiants de la filière
    student_role = Role.query.filter_by(name='etudiant').first()
    students = User.query.filter_by(track_id=track.id, role_id=student_role.id).all()
    
    total_enrollments = 0
    for subject in subjects:
        for student in students:
            if subject not in student.enrolled_subjects:
                student.enrolled_subjects.append(subject)
                total_enrollments += 1
    
    db.session.commit()
    
    flash(f'{total_enrollments} inscription(s) effectuée(s) pour {len(students)} étudiant(s) sur {len(subjects)} matière(s).', 'success')
    return redirect(url_for('track.manage_subjects'))
