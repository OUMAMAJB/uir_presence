from app import create_app, db
from app.models import Role, User

app = create_app()

def seed_database():
    with app.app_context():
        # Create Roles
        roles = ['admin', 'admin_dept', 'admin_filiere', 'enseignant', 'etudiant']
        for role_name in roles:
            if not Role.query.filter_by(name=role_name).first():
                role = Role(name=role_name)
                db.session.add(role)
        
        db.session.commit()
        print("Roles created.")

        # Create Admin User
        admin_role = Role.query.filter_by(name='admin').first()
        if not User.query.filter_by(email='admin@uir.ac.ma').first():
            admin = User(
                email='admin@uir.ac.ma',
                password_hash='admin123', # In real app, hash this!
                first_name='Super',
                last_name='Admin',
                role_id=admin_role.id
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: admin@uir.ac.ma / admin123")
        else:
            print("Admin user already exists.")

if __name__ == '__main__':
    seed_database()
