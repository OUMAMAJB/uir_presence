"""
Script de migration pour le système à 5 comptes
Ajoute les nouveaux champs et met à jour les rôles
"""

from app import create_app, db
from app.models import Role, User
from sqlalchemy import text

app = create_app()

def migrate_database():
    with app.app_context():
        print("🔄 Début de la migration...")
        
        # 1. Ajouter les colonnes manquantes si elles n'existent pas
        print("\n📊 Vérification des colonnes...")
        
        try:
            # Vérifier si academic_year existe
            result = db.session.execute(text("SHOW COLUMNS FROM users LIKE 'academic_year'"))
            if not result.fetchone():
                print("  ➕ Ajout de la colonne 'academic_year' à la table users...")
                db.session.execute(text("ALTER TABLE users ADD COLUMN academic_year INT NULL"))
                db.session.commit()
                print("  ✅ Colonne 'academic_year' ajoutée")
            else:
                print("  ✓ Colonne 'academic_year' existe déjà")
                
            # Vérifier si teacher_id existe dans sessions
            result = db.session.execute(text("SHOW COLUMNS FROM sessions LIKE 'teacher_id'"))
            if not result.fetchone():
                print("  ➕ Ajout de la colonne 'teacher_id' à la table sessions...")
                db.session.execute(text("ALTER TABLE sessions ADD COLUMN teacher_id INT NULL"))
                db.session.execute(text("ALTER TABLE sessions ADD FOREIGN KEY (teacher_id) REFERENCES users(id)"))
                db.session.commit()
                print("  ✅ Colonne 'teacher_id' ajoutée")
            else:
                print("  ✓ Colonne 'teacher_id' existe déjà")
                
            # Vérifier si started_at existe dans sessions
            result = db.session.execute(text("SHOW COLUMNS FROM sessions LIKE 'started_at'"))
            if not result.fetchone():
                print("  ➕ Ajout de la colonne 'started_at' à la table sessions...")
                db.session.execute(text("ALTER TABLE sessions ADD COLUMN started_at DATETIME NULL"))
                db.session.commit()
                print("  ✅ Colonne 'started_at' ajoutée")
            else:
                print("  ✓ Colonne 'started_at' existe déjà")
                
            # Vérifier si stopped_at existe dans sessions
            result = db.session.execute(text("SHOW COLUMNS FROM sessions LIKE 'stopped_at'"))
            if not result.fetchone():
                print("  ➕ Ajout de la colonne 'stopped_at' à la table sessions...")
                db.session.execute(text("ALTER TABLE sessions ADD COLUMN stopped_at DATETIME NULL"))
                db.session.commit()
                print("  ✅ Colonne 'stopped_at' ajoutée")
            else:
                print("  ✓ Colonne 'stopped_at' existe déjà")
                
        except Exception as e:
            print(f"  ❌ Erreur lors de l'ajout des colonnes: {e}")
            db.session.rollback()
            return False
        
        # 2. Créer/Vérifier les rôles
        print("\n👥 Vérification des rôles...")
        
        roles_needed = [
            ('super_admin', 'Super Administrateur - Accès complet'),
            ('admin_dept', 'Chef de Département'),
            ('admin_filiere', 'Chef de Filière'),
            ('enseignant', 'Enseignant Titulaire'),
            ('etudiant', 'Étudiant')
        ]
        
        for role_name, description in roles_needed:
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                role = Role(name=role_name)
                db.session.add(role)
                print(f"  ➕ Rôle '{role_name}' créé")
            else:
                print(f"  ✓ Rôle '{role_name}' existe déjà")
        
        db.session.commit()
        
        # 3. Migrer le rôle 'admin' vers 'super_admin' si nécessaire
        print("\n🔄 Migration des rôles existants...")
        
        old_admin_role = Role.query.filter_by(name='admin').first()
        super_admin_role = Role.query.filter_by(name='super_admin').first()
        
        if old_admin_role and super_admin_role:
            # Migrer tous les utilisateurs 'admin' vers 'super_admin'
            admin_users = User.query.filter_by(role_id=old_admin_role.id).all()
            if admin_users:
                print(f"  🔄 Migration de {len(admin_users)} utilisateur(s) admin vers super_admin...")
                for user in admin_users:
                    user.role_id = super_admin_role.id
                db.session.commit()
                print(f"  ✅ {len(admin_users)} utilisateur(s) migré(s)")
            
            # Supprimer l'ancien rôle 'admin'
            print("  🗑️ Suppression de l'ancien rôle 'admin'...")
            db.session.delete(old_admin_role)
            db.session.commit()
            print("  ✅ Ancien rôle 'admin' supprimé")
        else:
            print("  ✓ Aucune migration de rôle nécessaire")
        
        print("\n✅ Migration terminée avec succès !")
        print("\n📋 Résumé des rôles:")
        all_roles = Role.query.all()
        for role in all_roles:
            user_count = User.query.filter_by(role_id=role.id).count()
            print(f"  - {role.name}: {user_count} utilisateur(s)")
        
        return True

if __name__ == '__main__':
    success = migrate_database()
    if success:
        print("\n🎉 Vous pouvez maintenant utiliser le système à 5 comptes !")
    else:
        print("\n❌ La migration a échoué. Veuillez vérifier les erreurs ci-dessus.")
