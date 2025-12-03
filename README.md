# UIR Presence - Plateforme de Gestion de Présence Universitaire

## 📋 Vue d'ensemble

Cette plateforme complète permet de gérer la présence des étudiants à l'Université Internationale de Rabat avec un système de rôles hiérarchiques et des fonctionnalités avancées.

## 🎯 Fonctionnalités Implémentées

### 1. Système de Rôles et Permissions

#### **Super Admin (admin)**
- ✅ Accès complet à toutes les fonctionnalités
- ✅ Création de départements
- ✅ Ajout d'enseignants (manuel + import Excel)
- ✅ Assignation des chefs de département
- ✅ Vue consolidée de tous les départements et enseignants

#### **Admin Département (admin_dept)**
- ✅ Création de filières dans son département
- ✅ Gestion des enseignants de la filière
- ✅ Assignation des chefs de filière
- ✅ Vue des statistiques du département

#### **Admin Filière (admin_filiere)**
- ✅ Création de matières avec quotas horaires (CM/TD/TP)
- ✅ Affectation des enseignants aux matières
- ✅ Ajout d'étudiants (manuel + import Excel)
- ✅ Vue des statistiques de la filière

#### **Enseignant (enseignant)**
- ✅ Vue de tous ses cours assignés
- ✅ Création de sessions de cours avec type (CM/TD/TP)
- ✅ Génération de QR Code dynamique pour chaque session
- ✅ Rafraîchissement automatique du QR toutes les 15 secondes
- ✅ Démarrage/arrêt de sessions
- ✅ Visualisation des listes de présence

#### **Étudiant (etudiant)**
- ✅ Scan de QR Code via caméra (html5-qrcode)
- ✅ Enregistrement automatique de la présence
- ✅ Vue de tous ses cours et statistiques d'assiduité
- ✅ Calcul automatique du pourcentage d'absence par matière
- ✅ **Statut Rattrapage** si absence > 30%

### 2. Sécurité

✅ **Hachage sécurisé des mots de passe** avec Werkzeug
✅ **Tokens de réinitialisation** sécurisés et temporaires (expiration 24h-72h)
✅ **QR Codes dynamiques** avec tokens uniques et expiration automatique
✅ **Contraintes d'accès** par rôle sur toutes les routes
✅ **Validation d'appartenance** (chef doit être du département/filière)

### 3. Gestion des Utilisateurs

✅ **Création d'enseignants** :
  - Formulaire manuel
  - Import Excel (colonnes : First Name, Last Name, Email, Department)
  - Envoi automatique d'email avec lien de création de mot de passe
  
✅ **Création d'étudiants** :
  - Formulaire manuel
  - Import Excel (colonnes : First Name, Last Name, Email)
  - Assignation automatique à la filière
  - Envoi automatique d'email

### 4. Structure Académique

✅ **Années Académiques** (ex: 2024-2025)
✅ **Semestres** (S1 à S6)
✅ **Départements** avec chef assignable
✅ **Filières** avec chef assignable
✅ **Matières** avec quotas horaires par type de session
✅ **Affectation Many-to-Many** des enseignants aux filières et matières

### 5. Gestion des Présences

✅ **Sessions de cours** avec :
  - Type (CM, TD, TP)
  - Date et horaires
  - QR Code dynamique
  - Statut actif/inactif

✅ **Enregistrement de présence** :
  - Scan QR Code en temps réel
  - Validation de l'inscription à la matière
  - Prévention des doubles scans
  - Horodatage précis

✅ **Statistiques d'assiduité** :
  - Calcul automatique par matière
  - Pourcentage d'absence
  - Détermination du statut (Normal/Rattrapage)

### 6. Communication

✅ **Intégration Gmail** :
  - Configuration SMTP sécurisée
  - Templates HTML professionnels
  - Envoi d'emails de bienvenue
  - Liens de création de mot de passe
  - Gestion des erreurs d'envoi

### 7. Interface Utilisateur

✅ **Design moderne et professionnel** :
  - Palette de couleurs UIR (Primary, Secondary, Accent)
  - Dégradés et animations
  - Design responsive (mobile-first)
  - Cartes interactives avec hover effects
  - Tableaux de données clairs

✅ **Dashboards personnalisés** par rôle
✅ **Navigation intuitive** avec breadcrumbs
✅ **Feedback visuel** (flash messages, loading states)

## 📁 Structure du Projet

```
uir presence/
├── app/
│   ├── __init__.py              # Initialisation Flask & blueprints
│   ├── models.py                # Modèles SQLAlchemy (12 tables)
│   ├── routes/
│   │   ├── auth.py              # Authentification
│   │   ├── admin.py             # Super Admin
│   │   ├── department.py        # Admin Département
│   │   ├── track.py             # Admin Filière
│   │   ├── teacher.py           # Enseignant
│   │   ├── student.py           # Étudiant
│   │   └── import_export.py     # Import Excel
│   └── templates/
│       ├── base.html            # Template de base
│       ├── auth/               # Login, set password
│       ├── admin/              # Dashboards admin
│       ├── department/         # Gestion département
│       ├── track/              # Gestion filière
│       ├── teacher/            # Gestion cours
│       └── student/            # Dashboard & scan
├── migrations/                  # Migrations Alembic
├── config.py                    # Configuration
├── app.py                       # Point d'entrée
├── seed_data.py                 # Peuplement initial
├── .env                         # Variables d'environnement
├── requirements.txt             # Dépendances
└── GMAIL_SETUP.md              # Guide Gmail

```

## 🗄️ Modèle de Données

### Tables Principales
1. **users** - Utilisateurs (tous rôles)
2. **roles** - Rôles système
3. **departments** - Départements
4. **tracks** - Filières
5. **subjects** - Matières
6. **academic_years** - Années académiques
7. **semesters** - Semestres
8. **sessions** - Sessions de cours
9. **attendances** - Enregistrements de présence
10. **password_reset_tokens** - Tokens de réinitialisation

### Tables d'Association (Many-to-Many)
11. **enrollments** - Étudiants ↔ Matières
12. **teaching_assignments** - Enseignants ↔ Matières
13. **track_teachers** - Enseignants ↔ Filières

## 🚀 Installation et Lancement

### 1. Prérequis
```bash
Python 3.8+
MySQL Server
```

### 2. Installation
```bash
# Cloner le projet
cd "uir presence"

# Créer l'environnement virtuel
python -m venv venv
.\venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configuration

Créer `.env` :
```env
SECRET_KEY=votre-clé-secrète
DATABASE_URL=mysql+pymysql://root:password@localhost/uir_presence
MAIL_PASSWORD=votre-app-password-gmail
```

Configurer Gmail (voir GMAIL_SETUP.md)

### 4. Initialisation BDD
```bash
# Créer la base de données
flask db upgrade

# Peupler les données initiales
python seed_data.py
```

### 5. Créer le Super Admin
```python
python
>>> from app import create_app, db
>>> from app.models import User, Role
>>> app = create_app()
>>> with app.app_context():
...     admin_role = Role.query.filter_by(name='admin').first()
...     admin = User(email='admin@uir.ac.ma', first_name='Admin', last_name='UIR', role_id=admin_role.id)
...     admin.set_password('admin123')
...     db.session.add(admin)
...     db.session.commit()
```

### 6. Lancer l'application
```bash
python app.py
# ou
flask run
```

Accéder à : `http://localhost:5000`

## 📧 Configuration Email

Voir `GMAIL_SETUP.md` pour :
- Activer l'authentification à 2 facteurs
- Générer un mot de passe d'application
- Configurer MAIL_PASSWORD dans .env

## 🔑 Comptes de Test

**Super Admin**
- Email: admin@uir.ac.ma
- Password: admin123

Les autres comptes sont créés via l'interface admin et reçoivent un email pour définir leur mot de passe.

## 📊 Flux de Travail

### Workflow Super Admin
1. Créer des départements
2. Ajouter des enseignants (manuel ou Excel)
3. Assigner un chef de département
4. Le chef peut ensuite créer des filières

### Workflow Chef de Département
1. Créer des filières
2. Affecter des enseignants aux filières
3. Assigner un chef de filière

### Workflow Chef de Filière
1. Créer des matières avec quotas
2. Affecter des enseignants aux matières
3. Ajouter des étudiants (manuel ou Excel)

### Workflow Enseignant
1. Voir ses matières assignées
2. Créer une session de cours
3. Démarrer la session → QR Code généré
4. Les étudiants scannent
5. Arrêter la session

### Workflow Étudiant
1. Scanner le QR Code de la session
2. Présence enregistrée automatiquement
3. Consulter son assiduité
4. Vérifier son statut (Normal/Rattrapage)

## 🎨 Palette de Couleurs

```css
Primary: #163A59 (Bleu foncé UIR)
Secondary: #5097C5 (Bleu moyen)
Accent: #A1A621 (Jaune/vert UIR)
Highlight: #D9CB04 (Jaune vif)
Light: #E5E7E2 (Gris clair)
```

## ⚠️ Notes Importantes

1. **Sécurité Production** :
   - Changer SECRET_KEY
   - Utiliser HTTPS
   - Ajouter rate limiting
   - Activer CSRF protection

2. **QR Codes** :
   - Rafraîchissement automatique toutes les 15s
   - Tokens invalidés à l'arrêt de session
   - Validation stricte (session active + inscription)

3. **Règle Rattrapage** :
   - Actuellement : > 30% d'absence
   - Modifiable dans `app/routes/student.py` ligne 57

4. **Import Excel** :
   - Format strictement requis
   - Colonnes sensibles à la casse
   - Validation des données obligatoire

## 🐛 Dépannage

**Email ne s'envoie pas** :
- Vérifier MAIL_PASSWORD dans .env
- Vérifier que l'authentification 2FA est active
- Vérifier le mot de passe d'application

**QR Code ne scanne pas** :
- Vérifier que la session est active
- Autoriser l'accès caméra dans le navigateur
- Vérifier que l'étudiant est inscrit au cours

**Erreur de migration** :
- `flask db stamp head` pour resynchroniser
- Vérifier la base de données MySQL

## 📝 Prochaines Améliorations Suggérées

- [ ] Statistiques avancées (graphiques, exports)
- [ ] Notifications push pour les sessions
- [ ] Gestion des rattrapages (nouvelle session)
- [] API REST pour mobile app
- [ ] Système de notes intégré
- [] Génération de rapports PDF
- [ ] Dashboard analytics pour admin
- [ ] Historique d'actions (audit log)

## 📄 Licence

Projet propriétaire - Université Internationale de Rabat © 2024

---

**Développé pour l'UIR avec ❤️**
