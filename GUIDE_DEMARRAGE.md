# 🚀 Guide de Démarrage Rapide - UIR Presence

## Pour l'Administrateur Système

### 1️⃣ Première Connexion en tant que Super Admin

Accédez à : `http://localhost:5000` ou `http://127.0.0.1:5000`

**Identifiants par défaut** :
- Email : `admin@uir.ac.ma`
- Mot de passe : `admin123`

⚠️ **Important** : Changez ce mot de passe immédiatement après la première connexion !

Pour changer le mot de passe :
1. Déconnectez-vous
2. Cliquez sur "Mot de passe oublié ?"
3. Entrez `admin@uir.ac.ma`
4. Consultez votre email pour le lien de réinitialisation

---

## 📋 Workflow Initial de Configuration

### Étape 1 : Créer les Départements

1. Depuis le **Dashboard Super Admin**
2. Cliquer sur **"Nouveau Département"**
3. Exemples de départements :
   - Informatique
   - Génie Civil
   - Commerce & Gestion
   - Architecture
   - etc.

### Étape 2 : Ajouter les Enseignants

#### Option A : Ajout Manuel (pour quelques enseignants)
1. Cliquer sur **"Ajouter Enseignant"** → **"Manuel"**
2. Remplir le formulaire :
   - Prénom
   - Nom
   - Email
   - Département
3. L'enseignant reçoit un email pour créer son mot de passe

#### Option B : Import Excel (pour plusieurs enseignants)
1. Cliquer sur **"Ajouter Enseignant"** → **"Excel"**
2. Préparer un fichier Excel avec ces colonnes exactes :
   ```
   First Name | Last Name | Email              | Department
   Hassan     | Benali    | h.benali@uir.ac.ma | Informatique
   Amina      | El Fassi  | a.fassi@uir.ac.ma  | Informatique
   Said       | Tazi      | s.tazi@uir.ac.ma   | Génie Civil
   ```
3. ⚠️ **Colonnes obligatoires** (respect de la casse) :
   - `First Name`
   - `Last Name`
   - `Email`
   - `Department` (doit correspondre EXACTEMENT à un département existant)
4. Télécharger le fichier
5. Tous les enseignants reçoivent un email automatiquement

### Étape 3 : Assigner les Chefs de Département

1. Dans le **Dashboard Super Admin**
2. Descendre à la section **"Départements & Enseignants"**
3. Pour chaque département :
   - Ouvrir le dropdown "Chef de Département"
   - Sélectionner un enseignant du département
   - Cliquer sur ✓
4. L'enseignant sélectionné devient **Chef de Département** (`admin_dept`)

---

## 👨‍💼 Pour le Chef de Département

### Première Connexion
1. Consulter l'email reçu
2. Cliquer sur "Créer mon mot de passe"
3. Définir un mot de passe sécurisé
4. Se connecter à la plateforme

### Tâches Principales

#### 1. Créer les Filières
1. Dashboard Département → **"Nouvelle Filière"**
2. Exemples pour le département Informatique :
   - Génie Logiciel
   - Réseaux & Sécurité
   - Intelligence Artificielle
   - Systèmes Embarqués

#### 2. Affecter les Enseignants aux Filières
1. Dans la table des filières
2. Cliquer sur **"Gérer Enseignants"**
3. Cocher les enseignants qui enseigneront dans cette filière
4. Un enseignant peut être dans **plusieurs filières**
5. Enregistrer

#### 3. Assigner les Chefs de Filière
1. Dans la table des filières
2. Dropdown "Chef de Filière"
3. Sélectionner un enseignant du département
4. Cliquer sur ✓
5. L'enseignant devient **Chef de Filière** (`admin_filiere`)

---

## 🎓 Pour le Chef de Filière

### Tâches Principales

#### 1. Créer les Matières avec Quotas
1. Dashboard Filière → **"Nouvelle Matière"**
2. Remplir :
   - **Nom** : ex. "Programmation Java"
   - **Semestre** : S1 à S6
   - **Sessions CM** : ex. 20 (heures de cours magistraux)
   - **Sessions TD** : ex. 15 (heures de travaux dirigés)
   - **Sessions TP** : ex. 10 (heures de travaux pratiques)
3. Créer

#### 2. Affecter les Enseignants aux Matières
1. Table des matières → **"Gérer Enseignants"**
2. Cocher les enseignants qui enseigneront cette matière
3. ⚠️ Seuls les enseignants **affectés à la filière** sont disponibles
4. Enregistrer

#### 3. Ajouter les Étudiants

**Option A : Ajout Manuel**
1. **"Ajouter Étudiant"** → **"Manuel"**
2. Remplir le formulaire
3. L'étudiant reçoit un email

**Option B : Import Excel**
1. **"Ajouter Étudiant"** → **"Excel"**
2. Fichier Excel avec colonnes :
   ```
   First Name | Last Name | Email
   Mohamed    | Alaoui    | m.alaoui@uir.ac.ma
   Sara       | Benkirane | s.benkirane@uir.ac.ma
   ```
3. Colonnes obligatoires : `First Name`, `Last Name`, `Email`
4. Tous assignés automatiquement à la filière

---

## 👨‍🏫 Pour l'Enseignant

### Utilisation au Quotidien

#### 1. Voir Mes Cours
- Dashboard Enseignant affiche toutes les matières assignées
- Cliquer sur une matière pour voir les détails

#### 2. Créer une Session de Cours
1. Dans les détails du cours → **"Nouvelle Session"**
2. Remplir :
   - **Type** : CM / TD / TP
   - **Date** : ex. 2024-12-15
   - **Heure début** : ex. 08:00
   - **Heure fin** : ex. 10:00
3. Créer

#### 3. Démarrer la Session et Générer le QR Code
1. Liste des sessions → **"QR Code"**
2. Cliquer sur **"Démarrer la Session"**
3. Un QR Code apparaît
4. **Rafraîchissement automatique toutes les 15 secondes** (sécurité)
5. Les étudiants scannent
6. Cliquer sur **"Arrêter la Session"** à la fin du cours

---

## 🎒 Pour l'Étudiant

### Utilisation

#### 1. Scanner le QR Code
1. Dashboard Étudiant → **"Scanner QR Code"**
2. Autoriser l'accès à la caméra
3. Pointer la caméra vers le QR Code affiché par l'enseignant
4. Message de confirmation de présence

#### 2. Consulter Mon Assiduité
- Dashboard affiche toutes les matières
- Pour chaque matière :
  - Nombre de sessions totales
  - Nombre de présences
  - Nombre d'absences
  - **Pourcentage d'absence**
  - **Statut** : Normal ou **Rattrapage** (si > 30% d'absence)

---

## ❓ Problèmes Courants et Solutions

### 🔴 Je n'ai pas reçu l'email

**Causes possibles** :
1. Vérifier le dossier **Spam/Courrier indésirable**
2. Vérifier que l'email est correct
3. Vérifier la configuration Gmail du serveur (voir `GMAIL_SETUP.md`)

**Solution** :
- Demander au Super Admin/Chef de renvoyer l'invitation
- Ou utiliser "Mot de passe oublié" sur la page de login

### 🔴 Le QR Code ne scanne pas

**Solutions** :
1. Vérifier que la session est **démarrée** (bouton vert "En cours")
2. Autoriser l'accès caméra dans le navigateur
3. Vérifier que vous êtes bien **inscrit** à cette matière
4. Rafraîchir la page
5. Utiliser un autre navigateur (Chrome/Firefox recommandés)

### 🔴 Erreur "Email existe déjà"

**Cause** : L'utilisateur a déjà un compte

**Solution** :
- Ne pas recréer le compte
- Demander à l'utilisateur d'utiliser "Mot de passe oublié"

### 🔴 Import Excel échoue

**Vérifications** :
1. **Colonnes exactes** (sensibles à la casse) :
   - Enseignants : `First Name`, `Last Name`, `Email`, `Department`
   - Étudiants : `First Name`, `Last Name`, `Email`
2. **Format du fichier** : `.xlsx` ou `.xls`
3. **Département existe** (pour enseignants)
4. **Pas de doublons** d'email

---

## 📊 Exemple de Déploiement Complet

```
Université UIR
│
├─ 📁 Département : Informatique
│  │
│  ├─ 👤 Chef Département : Prof. Hassan Benali
│  ├─ 👥 Enseignants : 15 profs
│  │
│  ├─ 📚 Filière : Génie Logiciel (S1-S6)
│  │  ├─ 👤 Chef Filière : Dr. Amina El Fassi
│  │  ├─ 👥 Enseignants affectés : 8 profs
│  │  ├─ 👨‍🎓 Étudiants : 120 étudiants
│  │  └─ 📖 Matières (Exemples) :
│  │     ├─ Programmation Java (S2) - CM:20h, TD:15h, TP:10h
│  │     ├─ Base de Données (S3) - CM:25h, TD:20h, TP:15h
│  │     └─ Architecture Logicielle (S5) - CM:25h, TD:20h, TP:0h
│  │
│  └─ 📚 Filière : Intelligence Artificielle (S1-S6)
│     ├─ 👤 Chef Filière : Dr. Said Tazi
│     ├─ 👥 Enseignants affectés : 10 profs
│     ├─ 👨‍🎓 Étudiants : 80 étudiants
│     └─ 📖 Matières : Machine Learning, Deep Learning, etc.
│
└─ 📁 Département : Génie Civil
   ├─ 👤 Chef Département : Prof. Karim Alaoui
   └─ ... (même structure)
```

---

## 🎯 Checklist de Mise en Production

- [ ] Changer le mot de passe Super Admin par défaut
- [ ] Configurer Gmail avec un App Password (voir `GMAIL_SETUP.md`)
- [ ] Définir `SECRET_KEY` unique dans `.env`
- [ ] Créer tous les départements
- [ ] Importer ou ajouter tous les enseignants
- [ ] Assigner les chefs de département
- [ ] Les chefs créent les filières
- [ ] Les chefs assignent les chefs de filière
- [ ] Les chefs de filière créent les matières
- [ ] Les chefs de filière ajoutent les étudiants
- [ ] Les enseignants créent leurs sessions
- [ ] Tester le scan QR Code
- [ ] Vérifier les emails reçus
- [ ] Former les utilisateurs

---

## 📞 Support

Pour toute assistance :
1. Consulter `README.md` - Documentation complète
2. Consulter `TYPES_COMPTES_ADMIN.md` - Détails des permissions
3. Consulter `GMAIL_SETUP.md` - Configuration email
4. Contacter l'administrateur système UIR

---

**Bonne utilisation de UIR Presence ! 🎓✨**
