from app import create_app, db
from app.models import User, Role
from werkzeug.security import generate_password_hash

# -------------------------------
# 📌 1) Liste des rôles à créer
# -------------------------------
DEFAULT_ROLES = [
    "admin",            # admin principal
    "admin_dept",       # chef de département
    "admin_filiere",    # chef de filière
    "enseignant",       # professeur
    "etudiant"          # élève
]


# -----------------------------------------
# 📌 2) Créer automatiquement tous les rôles
# -----------------------------------------
def create_roles():
    for role_name in DEFAULT_ROLES:
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            new_role = Role(name=role_name)
            db.session.add(new_role)
            print(f"✔ Rôle créé : {role_name}")
    db.session.commit()


# ---------------------------------------------------
# 📌 3) Créer l'admin principal s'il n'existe pas déjà
# ---------------------------------------------------
def create_super_admin():
    # Récupérer le rôle admin
    admin_role = Role.query.filter_by(name="admin").first()

    # Vérifier si un utilisateur avec ce rôle existe
    existing_admin = User.query.filter_by(role_id=admin_role.id).first()

    if existing_admin:
        print("ℹ Admin principal existe déjà.")
        return

    # Créer un super admin
    admin = User(
        email="oumaimajb4@gmail.com",
        first_name="Super",
        last_name="Admin",
        password_hash=generate_password_hash("123"),
        role_id=admin_role.id
    )

    db.session.add(admin)
    db.session.commit()

    print("✔ Super admin créé avec succès !")
    print("Login : oumaimajb4@gmail.com")
    print("Password : 123")


# -------------------------------------------------
# 📌 4) Exécuter tout lorsque le script est lancé
# -------------------------------------------------
if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        db.create_all()
        print("✔ Tables créées.")

        create_roles()
        create_super_admin()

        print("🎉 Initialisation terminée.")
