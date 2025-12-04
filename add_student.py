"""
Script pour ajouter un étudiant à la base de données
"""

from app import create_app, db
from app.models import User, Role

app = create_app()

with app.app_context():
    # Récupérer le rôle étudiant
    student_role = Role.query.filter_by(name='etudiant').first()
    
    if not student_role:
        print("❌ Le rôle 'etudiant' n'existe pas. Création du rôle...")
        student_role = Role(name='etudiant')
        db.session.add(student_role)
        db.session.commit()
        print("✅ Rôle 'etudiant' créé")
    
    # Vérifier si l'étudiant existe déjà
    existing_student = User.query.filter_by(email='aliballacherif@gmail.com').first()
    
    if existing_student:
        print(f"⚠️  L'utilisateur {existing_student.email} existe déjà")
        print(f"   Mise à jour du mot de passe...")
        existing_student.set_password('123')
        db.session.commit()
        print("✅ Mot de passe mis à jour!")
    else:
        # Créer le nouvel étudiant
        student = User(
            email='aliballacherif@gmail.com',
            first_name='Ali',
            last_name='Ballacherif',
            role_id=student_role.id,
            track_id=None,  # À assigner plus tard
            academic_year=1
        )
        student.set_password('123')
        
        db.session.add(student)
        db.session.commit()
        
        print("✅ Étudiant créé avec succès!")
        print(f"   Email: {student.email}")
        print(f"   Nom: {student.first_name} {student.last_name}")
        print(f"   Rôle: {student.role.name}")
        print(f"   Mot de passe: 123")
    
    print("\n🔐 Vous pouvez maintenant vous connecter avec:")
    print(f"   Email: aliballacherif@gmail.com")
    print(f"   Mot de passe: 123")
