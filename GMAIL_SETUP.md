# Configuration Gmail pour UIR Presence

## ⚙️ Étapes pour configurer l'authentification Gmail

### 1. Activer la validation en deux étapes
1. Allez sur [Google Account Security](https://myaccount.google.com/security)
2. Connectez-vous avec **oumaimajabrane23@gmail.com**
3. Sous "Se connecter à Google", activez la **Validation en deux étapes**

### 2. Générer un mot de passe d'application
1. Retournez sur [Google Account Security](https://myaccount.google.com/security)
2. Sous "Se connecter à Google", cliquez sur **Mots de passe des applications**
3. Dans "Sélectionner l'application", choisissez **Autre (nom personnalisé)**
4. Entrez **"UIR Presence"** comme nom
5. Cliquez sur **Générer**
6. Google va générer un mot de passe de 16 caractères
7. **Copiez ce mot de passe**

### 3. Configurer l'application
1. Ouvrez le fichier `.env` à la racine du projet
2. Remplacez `votre-mot-de-passe-application-gmail-ici` par le mot de passe généré
3. Le fichier devrait ressembler à :
```
MAIL_PASSWORD=abcd efgh ijkl mnop
```
(Avec votre mot de passe réel, pas cet exemple)

### 4. Installer Flask-Mail
Si ce n'est pas déjà fait, exécutez :
```bash
.\venv\Scripts\pip install Flask-Mail
```

### 5. Redémarrer l'application
Arrêtez l'application Flask (Ctrl+C) et relancez-la :
```bash
.\venv\Scripts\python app.py
```

## 📧 Fonctionnalités Email

Une fois configuré, le système pourra :
- ✉️ Envoyer des emails de bienvenue aux nouveaux utilisateurs
- 🔑 Envoyer des liens de réinitialisation de mot de passe
- 📊 Envoyer des rapports de présence
- ⚠️ Envoyer des alertes de rattrapage aux étudiants

## 🔒 Sécurité

- ⚠️ **IMPORTANT** : Ne partagez jamais votre mot de passe d'application
- Le fichier `.env` est ignoré par Git (déjà dans `.gitignore`)
- En production, utilisez des variables d'environnement serveur

## 🧪 Tester l'envoi d'email

Vous pouvez tester l'envoi d'email avec ce script Python :
```python
from flask_mail import Message
from app import create_app, mail

app = create_app()
with app.app_context():
    msg = Message(
        subject="Test UIR Presence",
        recipients=["votre-email@test.com"],
        body="Ceci est un email de test depuis UIR Presence!"
    )
    mail.send(msg)
    print("Email envoyé avec succès!")
```

## 📝 Notes
- Gmail SMTP: smtp.gmail.com
- Port: 587 (TLS)
- Sender: oumaimajabrane23@gmail.com
- Limite Gmail: ~500 emails/jour pour les comptes gratuits
