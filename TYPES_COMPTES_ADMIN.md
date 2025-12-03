# 🔐 Types de Comptes Administrateurs - UIR Presence

## Vue d'ensemble

Le système UIR Presence implémente **3 types de comptes administrateurs** avec des niveaux de permissions hiérarchiques distincts.

---

## 1. 👑 Super Admin (admin)

### Description
Le Super Admin a **un accès complet et illimité** à toutes les fonctionnalités de la plateforme. C'est le compte le plus puissant du système.

### Permissions & Fonctionnalités

#### ✅ Gestion des Départements
- Créer des départements
- Voir tous les départements
- Assigner/modifier les chefs de département
- Accéder aux statistiques globales

#### ✅ Gestion des Enseignants
- **Ajout Manuel** : Formulaire de création individuelle
- **Import Excel** : Import en masse depuis un fichier Excel
  - Colonnes requises : `First Name`, `Last Name`, `Email`, `Department`
  - Envoi automatique d'email avec lien de création de mot de passe
- Voir tous les enseignants par département
- Modifier les affectations

#### ✅ Accès Universel
- Accès à **tous** les dashboards (Département, Filière, Enseignant, Étudiant)
- Bypass automatique de toutes les restrictions de rôle
- Vue consolidée de toute l'université

#### ✅ Administration Système
- Gestion complète des utilisateurs
- Supervision de toutes les activités
- Accès aux logs et statistiques globales

### Interface
- **Dashboard Principal** : Vue d'ensemble avec :
  - Quick access cards vers tous les modules
  - Liste complète des départements avec leurs enseignants (toggle)
  - Formulaire d'assignation des chefs de département
  - Statistiques globales

### Comment créer un Super Admin
```python
from app import create_app, db
from app.models import User, Role

app = create_app()
with app.app_context():
    admin_role = Role.query.filter_by(name='admin').first()
    admin = User(
        email='admin@uir.ac.ma',
        first_name='Admin',
        last_name='UIR',
        role_id=admin_role.id
    )
    admin.set_password('VotreMotDePasse123!')
    db.session.add(admin)
    db.session.commit()
```

---

## 2. 🏛️ Chef de Département (admin_dept)

### Description
Le Chef de Département gère **un département spécifique** et toutes ses filières. Il est assigné par le Super Admin.

### Permissions & Fonctionnalités

#### ✅ Gestion des Filières
- **Créer des filières** dans son département
- Voir toutes les filières du département
- **Assigner des chefs de filière**
  - Le chef doit être un enseignant du département
  - Un ancien chef est automatiquement rétrogradé en enseignant

#### ✅ Gestion des Enseignants de Filière
- **Affecter des enseignants aux filières** (many-to-many)
  - Page dédiée avec checkboxes
  - Seuls les enseignants du département sont disponibles
- Voir la liste des enseignants du département

#### ✅ Vue Département
- Statistiques du département
- Liste de toutes les filières
- Nombre d'enseignants par filière

### Restrictions
- ❌ Ne peut PAS créer de départements
- ❌ Ne peut PAS gérer d'autres départements
- ❌ Limité à son département uniquement

### Comment assigner un Chef de Département
1. Le Super Admin va dans le **Dashboard Admin**
2. Dans la table "Départements & Enseignants"
3. Sélectionne un enseignant du département dans le dropdown
4. Clique sur ✓ pour valider
5. L'enseignant devient automatiquement **Chef de Département** (rôle `admin_dept`)
6. L'ancien chef (s'il y en avait un) redevient enseignant

### Interface
- **Dashboard Département** : Vue spécialisée avec :
  - Bouton "Nouvelle Filière"
  - Table des filières avec :
    - Dropdown pour assigner le chef de filière
    - Nombre d'enseignants par filière
    - Bouton "Gérer Enseignants"
  - Statistiques du département

---

## 3. 🎓 Chef de Filière (admin_filiere)

### Description
Le Chef de Filière gère **une filière spécifique** : matières, étudiants, et affectations d'enseignants. Il est assigné par le Chef de Département.

### Permissions & Fonctionnalités

#### ✅ Gestion des Matières
- **Créer des matières** avec :
  - Nom de la matière
  - Semestre (S1 à S6)
  - **Quotas horaires par type** :
    - Sessions CM (Cours Magistraux)
    - Sessions TD (Travaux Dirigés)
    - Sessions TP (Travaux Pratiques)
- **Affecter des enseignants aux matières**
  - Seuls les enseignants affectés à la filière sont disponibles
  - Relation many-to-many (plusieurs enseignants par matière possible)

#### ✅ Gestion des Étudiants
- **Ajout Manuel** : Formulaire individuel
- **Import Excel** : Import en masse
  - Colonnes requises : `First Name`, `Last Name`, `Email`
  - Assignation automatique à la filière
  - Envoi automatique d'email
- Voir tous les étudiants de la filière
- Statistiques d'inscription

#### ✅ Vue Filière
- Liste de toutes les matières
- Nombre d'enseignants par matière
- Liste des étudiants inscrits
- Statistiques de la filière

### Restrictions
- ❌ Ne peut PAS créer de filières
- ❌ Ne peut PAS gérer d'autres filières
- ❌ Limité à sa filière uniquement
- ❌ Ne peut affecter que les enseignants déjà dans la filière

### Comment assigner un Chef de Filière
1. Le Chef de Département va dans son **Dashboard Département**
2. Dans la table "Filières"
3. Sélectionne un enseignant du département dans le dropdown
4. Clique sur ✓ pour valider
5. L'enseignant devient automatiquement **Chef de Filière** (rôle `admin_filiere`)
6. Il est aussi assigné à cette filière (`track_id` mis à jour)

### Interface
- **Dashboard Filière** : Vue spécialisée avec :
  - Bouton "Nouvelle Matière"
  - Boutons "Ajouter Étudiant" (Manuel / Excel)
  - Table des matières avec :
    - Type de sessions et quotas
    - Nombre d'enseignants assignés
    - Bouton "Gérer Enseignants"
  - Liste des étudiants (toggle)
  - Statistiques de la filière

---

## 📊 Tableau Comparatif

| Fonctionnalité | Super Admin | Chef Département | Chef Filière |
|---|---|---|---|
| **Créer départements** | ✅ | ❌ | ❌ |
| **Assigner chef département** | ✅ | ❌ | ❌ |
| **Importer enseignants (Excel)** | ✅ | ❌ | ❌ |
| **Créer filières** | ✅ | ✅ (son dept) | ❌ |
| **Assigner chef filière** | ✅ | ✅ (son dept) | ❌ |
| **Affecter enseignants à filières** | ✅ | ✅ (son dept) | ❌ |
| **Créer matières** | ✅ | ✅ | ✅ (sa filière) |
| **Affecter enseignants à matières** | ✅ | ✅ | ✅ (sa filière) |
| **Ajouter étudiants** | ✅ | ✅ | ✅ (sa filière) |
| **Importer étudiants (Excel)** | ✅ | ✅ | ✅ (sa filière) |
| **Voir tous départements** | ✅ | ❌ | ❌ |
| **Voir toutes filières** | ✅ | ✅ (son dept) | ❌ |
| **Accès Dashboard Enseignant** | ✅ | ✅ | ✅ |
| **Accès Dashboard Étudiant** | ✅ | ✅ | ✅ |

---

## 🔄 Workflow Hiérarchique

```
1. Super Admin
   └─> Crée Département "Informatique"
   └─> Ajoute Enseignants au département (Manuel/Excel)
   └─> Assigne "Prof. Hassan" comme Chef de Département
       
2. Chef Département (Prof. Hassan)
   └─> Crée Filière "Génie Logiciel"
   └─> Affecte des enseignants à la filière
   └─> Assigne "Dr. Amina" comme Chef de Filière
       
3. Chef Filière (Dr. Amina)
   └─> Crée Matière "Programmation Java" (CM:20h, TD:15h, TP:10h)
   └─> Affecte des enseignants à la matière
   └─> Ajoute des étudiants (Manuel/Excel)
       
4. Enseignant
   └─> Voit ses matières assignées
   └─> Crée des sessions de cours
   └─> Génère QR Codes pour la présence
       
5. Étudiant
   └─> Scanne le QR Code
   └─> Consulte son assiduité
```

---

## 🔐 Connexion et Mot de Passe Oublié

### Première Connexion
- **Super Admin** : Créé manuellement via script Python
- **Autres comptes** : Reçoivent un email avec lien "Créer mon mot de passe"
  - Lien valide 72 heures
  - Définissent leur propre mot de passe sécurisé

### Mot de Passe Oublié
1. Cliquer sur **"Mot de passe oublié ?"** sur la page de login
2. Entrer son adresse email
3. Recevoir un email avec lien de réinitialisation
4. Lien valide 24 heures
5. Définir un nouveau mot de passe

---

## 🛡️ Sécurité

### Contraintes d'Attribution
- **Chef de Département** : DOIT être enseignant du département
- **Chef de Filière** : DOIT être enseignant du département de la filière
- Un chef qui change de poste redevient automatiquement enseignant
- Un seul chef par département/filière à la fois

### Isolation des Permissions
- Chaque admin ne voit QUE son périmètre
- Aucun bypass possible (sauf Super Admin)
- Validations strictes sur toutes les routes

### Mots de Passe
- Hachage sécurisé avec `werkzeug.security`
- Tokens de réinitialisation uniques et temporaires
- Aucun mot de passe stocké en clair

---

## 📧 Notifications Email

Tous les comptes administrateurs reçoivent :
- ✉️ **Email de bienvenue** avec lien de création de mot de passe
- ✉️ **Email de réinitialisation** si mot de passe oublié
- ✉️ Templates HTML professionnels avec design UIR
- ✉️ Liens sécurisés avec expiration automatique

---

## 💡 Bonnes Pratiques

1. **Super Admin** :
   - Créer UN seul compte par institution
   - Utiliser un mot de passe très fort
   - Ne pas partager les identifiants

2. **Chefs de Département** :
   - Choisir des enseignants expérimentés
   - Documenter les responsabilités
   - Rotation possible si nécessaire

3. **Chefs de Filière** :
   - Bien structurer les matières par semestre
   - Vérifier les quotas horaires
   - Tenir à jour la liste des étudiants

---

**Pour toute question ou assistance, contactez l'administrateur système UIR.**
