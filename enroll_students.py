"""
Script pour inscrire automatiquement tous les étudiants aux matières de leur filière
"""
from app import create_app, db
from app.models import User, Subject, Role

app = create_app()

with app.app_context():
    # Récupérer role étudiant
    student_role = Role.query.filter_by(name='etudiant').first()
    
    if not student_role:
        print("Rôle 'etudiant' introuvable!")
        exit(1)
    
    # Récupérer tous les étudiants
    students = User.query.filter_by(role_id=student_role.id).all()
    
    # Récupérer toutes les matières
    subjects = Subject.query.all()
    
    print(f"Trouvé {len(students)} étudiant(s) et {len(subjects)} matière(s)")
    
    total_enrollments = 0
    
    for student in students:
        print(f"\nÉtudiant: {student.email} - Filière: {student.track.name if student.track else 'Aucune'}")
        
        for subject in subjects:
            # Inscrire l'étudiant seulement aux matières de sa filière
            if student.track_id == subject.track_id:
                if subject not in student.enrolled_subjects:
                    student.enrolled_subjects.append(subject)
                    total_enrollments += 1
                    print(f"  ✓ Inscrit à: {subject.name}")
                else:
                    print(f"  - Déjà inscrit à: {subject.name}")
    
    db.session.commit()
    print(f"\n✅ Total: {total_enrollments} nouvelle(s) inscription(s) effectuée(s)")
