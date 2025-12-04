from dotenv import load_dotenv
import os

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

from app import create_app, db
from app.models import User, Role, Department, Track, Subject, Session, Attendance, PasswordResetToken

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': User, 
        'Role': Role, 
        'Department': Department, 
        'Track': Track, 
        'Subject': Subject, 
        'Session': Session, 
        'Attendance': Attendance,
        'PasswordResetToken': PasswordResetToken
    }

if __name__ == '__main__':
    app.run(debug=True)
