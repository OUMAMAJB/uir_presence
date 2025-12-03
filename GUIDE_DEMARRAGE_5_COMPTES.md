# 🚀 Guide de Démarrage - Système 5 Comptes

## Date: 3 Décembre 2024

---

## 📋 Vue d'Ensemble

Ce guide vous accompagne pour démarrer le nouveau système à **5 types de comptes** :

1. **Super Chef** (Super Admin)
2. **Chef de Département**
3. **Chef de Filière**
4. **Enseignant Titulaire**
5. **Étudiant**

---

## ⚠️ IMPORTANT - Avant de Commencer

### Prérequis
- ✅ Python 3.8+ installé
- ✅ MySQL/MariaDB en cours d'exécution
- ✅ Environnement virtuel activé
- ✅ Fichier `.env` configuré (surtout MAIL_PASSWORD pour Gmail)

---

## 🔧 ÉTAPE 1: Migration de la Base de Données

### 1.1 Exécuter le Script de Migration

```bash
# Activer l'environnement virtuel (si pas déjà fait)
.\venv\Scripts\activate

# Exécuter la migration
python migrate_to_5_accounts.py
```

### 1.2 Vérifier la Migration

Le script devrait afficher :
```
🔄 Début de la migration...

📊 Vérification des colonnes...
  ➕ Ajout de la colonne 'academic_year' à la table users...
  ✅ Colonne 'academic_year' ajoutée
  ➕ Ajout de la colonne 'teacher_id' à la table sessions...
  ✅ Colonne 'teacher_id' ajoutée
  ...

👥 Vérification des rôles...
  ➕ Rôle 'super_admin' créé
  ➕ Rôle 'admin_dept' créé
  ➕ Rôle 'admin_filiere' créé
  ✅ Rôle 'enseignant' existe déjà
  ✅ Rôle 'etudiant' existe déjà

🔄 Migration des rôles existants...
  🔄 Migration de 1 utilisateur(s) admin vers super_admin...
  ✅ 1 utilisateur(s) migré(s)
  🗑️ Suppression de l'ancien rôle 'admin'...
  ✅ Ancien rôle 'admin' supprimé

✅ Migration terminée avec succès !

📋 Résumé des rôles:
  - super_admin: 1 utilisateur(s)
  - admin_dept: 0 utilisateur(s)
  - admin_filiere: 0 utilisateur(s)
  - enseignant: X utilisateur(s)
  - etudiant: Y utilisateur(s)

🎉 Vous pouvez maintenant utiliser le système à 5 comptes !
```

### 1.3 En Cas d'Erreur

Si la migration échoue :
1. Vérifiez que MySQL/MariaDB est en cours d'exécution
2. Vérifiez les credentials dans `.env`
3. Vérifiez les logs d'erreur affichés
4. Contactez le support si nécessaire

---

## 🚀 ÉTAPE 2: Démarrer l'Application

```bash
# Démarrer le serveur Flask
python app.py
```

L'application devrait démarrer sur `http://127.0.0.1:5000`

---

## 👤 ÉTAPE 3: Tester les Connexions

### 3.1 Connexion Super Admin

1. Allez sur `http://127.0.0.1:5000/auth/login`
2. Connectez-vous avec votre compte admin existant
3. Vous devriez être redirigé vers `/admin/dashboard`
4. ✅ Vérifiez que vous voyez le dashboard Super Admin

### 3.2 Créer un Chef de Département

**Depuis le dashboard Super Admin :**

1. Allez dans "Ajouter Enseignant"
2. Remplissez le formulaire :
   - Prénom: Jean
   - Nom: Dupont
   - Email: jean.dupont@uir.ac.ma
   - Département: (sélectionnez un département)
3. Cliquez "Add Teacher"
4. L'enseignant reçoit un email pour créer son mot de passe

**Nommer comme Chef de Département :**

1. Retournez au dashboard
2. Dans le tableau "Départements & Enseignants"
3. Sélectionnez l'enseignant dans la liste déroulante
4. Cliquez "Assigner Chef"
5. ✅ L'enseignant devient Chef de Département

### 3.3 Tester la Connexion Chef de Département

1. Déconnectez-vous
2. Connectez-vous avec le compte du chef de département
3. Vous devriez être redirigé vers `/department/dashboard`
4. ✅ Vérifiez que vous voyez le dashboard Chef de Département

### 3.4 Créer une Filière

**Depuis le dashboard Chef de Département :**

1. Cliquez sur "Créer une Filière"
2. Entrez le nom : "Génie Informatique"
3. Cliquez "Créer"
4. ✅ La filière apparaît dans le dashboard

### 3.5 Créer un Chef de Filière

1. Ajoutez un enseignant (via Super Admin ou Chef Dept)
2. Affectez-le à la filière
3. Nommez-le Chef de Filière
4. ✅ L'enseignant devient Chef de Filière

### 3.6 Tester la Connexion Chef de Filière

1. Connectez-vous avec le compte du chef de filière
2. Vous devriez être redirigé vers `/track/dashboard`
3. ✅ Vérifiez que vous voyez le dashboard Chef de Filière

### 3.7 Créer un Étudiant

**Depuis le dashboard Chef de Filière :**

1. Cliquez sur "Ajouter Étudiant"
2. Remplissez le formulaire :
   - Prénom: Marie
   - Nom: Martin
   - Email: marie.martin@uir.ac.ma
   - Année: 1
3. Cliquez "Ajouter"
4. L'étudiant reçoit un email pour créer son mot de passe

### 3.8 Tester la Connexion Étudiant

1. Connectez-vous avec le compte de l'étudiant
2. Vous devriez être redirigé vers `/student/dashboard`
3. ✅ Vérifiez que vous voyez le dashboard Étudiant

---

## 🧪 ÉTAPE 4: Tester les Fonctionnalités

### 4.1 Test Super Admin

- [ ] Créer un département
- [ ] Modifier un département
- [ ] Ajouter un enseignant
- [ ] Nommer un chef de département
- [ ] Consulter la liste des enseignants par département

### 4.2 Test Chef de Département

- [ ] Créer une filière
- [ ] Modifier une filière
- [ ] Nommer un chef de filière
- [ ] Affecter des enseignants aux filières
- [ ] Consulter la liste des étudiants par filière

### 4.3 Test Chef de Filière

- [ ] Créer une année académique
- [ ] Créer un semestre
- [ ] Créer une matière (avec CM, TD, TP)
- [ ] Affecter des enseignants aux matières
- [ ] Ajouter un étudiant
- [ ] Importer des étudiants (Excel)
- [ ] Consulter la liste des étudiants par année

### 4.4 Test Enseignant

- [ ] Voir ses matières affectées
- [ ] Créer une séance
- [ ] Démarrer une séance (QR code)
- [ ] Vérifier le rafraîchissement du QR (15s)
- [ ] Arrêter une séance
- [ ] Consulter l'historique des présences

### 4.5 Test Étudiant

- [ ] Voir ses matières
- [ ] Scanner un QR code
- [ ] Vérifier que la présence est enregistrée
- [ ] Consulter les statistiques personnelles
- [ ] Vérifier le calcul du statut (Admis/Rattrapage)
- [ ] Consulter l'historique détaillé d'une matière

---

## 📊 ÉTAPE 5: Vérifier les Permissions

### 5.1 Test de Sécurité

**Étudiant ne peut PAS :**
- [ ] Accéder à `/admin/dashboard` → Redirection
- [ ] Accéder à `/department/dashboard` → Redirection
- [ ] Accéder à `/track/dashboard` → Redirection
- [ ] Accéder à `/teacher/dashboard` → Redirection

**Enseignant ne peut PAS :**
- [ ] Accéder à `/admin/dashboard` → Redirection
- [ ] Accéder à `/department/dashboard` → Redirection
- [ ] Accéder à `/track/dashboard` → Redirection

**Chef de Filière PEUT :**
- [ ] Accéder à `/track/dashboard` ✅
- [ ] Accéder à `/teacher/dashboard` ✅ (héritage)

**Chef de Département PEUT :**
- [ ] Accéder à `/department/dashboard` ✅
- [ ] Accéder à `/track/dashboard` ✅ (héritage)
- [ ] Accéder à `/teacher/dashboard` ✅ (héritage)

**Super Admin PEUT :**
- [ ] Accéder à TOUS les dashboards ✅

---

## 📝 ÉTAPE 6: Import Excel

### 6.1 Template Excel pour Étudiants

Créez un fichier Excel avec les colonnes suivantes :

| First Name | Last Name | Email | Academic Year |
|------------|-----------|-------|---------------|
| Alice | Dubois | alice.dubois@uir.ac.ma | 1 |
| Bob | Martin | bob.martin@uir.ac.ma | 1 |
| Claire | Bernard | claire.bernard@uir.ac.ma | 2 |

### 6.2 Importer les Étudiants

1. Connectez-vous comme Chef de Filière
2. Allez dans "Importer Étudiants"
3. Sélectionnez le fichier Excel
4. Cliquez "Importer"
5. ✅ Vérifiez que les étudiants sont créés

---

## 🔍 ÉTAPE 7: Vérifier la Base de Données

### 7.1 Vérifier les Rôles

```bash
python inspect_db.py
```

Ou via MySQL :
```sql
SELECT * FROM roles;
```

Devrait afficher :
```
| id | name           |
|----|----------------|
| 1  | super_admin    |
| 2  | admin_dept     |
| 3  | admin_filiere  |
| 4  | enseignant     |
| 5  | etudiant       |
```

### 7.2 Vérifier les Utilisateurs

```sql
SELECT u.id, u.first_name, u.last_name, u.email, r.name as role
FROM users u
JOIN roles r ON u.role_id = r.id;
```

### 7.3 Vérifier les Nouvelles Colonnes

```sql
DESCRIBE users;
DESCRIBE sessions;
```

Devrait montrer :
- `users.academic_year` (INT, NULL)
- `sessions.teacher_id` (INT, NULL)
- `sessions.started_at` (DATETIME, NULL)
- `sessions.stopped_at` (DATETIME, NULL)

---

## 🐛 Dépannage

### Problème 1: Erreur de Migration

**Symptôme :** La migration échoue avec une erreur SQL

**Solution :**
1. Vérifiez que MySQL est en cours d'exécution
2. Vérifiez les credentials dans `.env`
3. Vérifiez que la base de données existe
4. Essayez de relancer la migration

### Problème 2: Redirection Incorrecte

**Symptôme :** Après login, redirection vers une mauvaise page

**Solution :**
1. Vérifiez le rôle de l'utilisateur dans la base de données
2. Vérifiez que `app/decorators.py` est bien importé
3. Vérifiez que `get_dashboard_for_role()` retourne la bonne URL

### Problème 3: Permissions Refusées

**Symptôme :** Message "Accès refusé" alors que l'utilisateur devrait avoir accès

**Solution :**
1. Vérifiez le rôle de l'utilisateur
2. Vérifiez le décorateur utilisé sur la route
3. Vérifiez la hiérarchie des permissions dans `decorators.py`

### Problème 4: Email Non Envoyé

**Symptôme :** L'utilisateur ne reçoit pas l'email de création de mot de passe

**Solution :**
1. Vérifiez que `MAIL_PASSWORD` est configuré dans `.env`
2. Vérifiez que c'est un mot de passe d'application Gmail
3. Vérifiez les spams/courrier indésirable
4. Vérifiez les logs de l'application

---

## 📚 Documentation Complémentaire

- **Spécifications complètes** : `SPECIFICATIONS_5_COMPTES.md`
- **Plan d'implémentation** : `PLAN_IMPLEMENTATION.md`
- **Modifications effectuées** : `MODIFICATIONS_3_DEC_2024.md`
- **Configuration Gmail** : `GMAIL_SETUP.md`

---

## ✅ Checklist Finale

Avant de considérer le système comme opérationnel :

- [ ] Migration exécutée avec succès
- [ ] 5 rôles créés dans la base de données
- [ ] Super Admin peut se connecter
- [ ] Chef de Département peut se connecter
- [ ] Chef de Filière peut se connecter
- [ ] Enseignant peut se connecter
- [ ] Étudiant peut se connecter
- [ ] Redirections fonctionnent correctement
- [ ] Permissions respectées
- [ ] QR code fonctionne
- [ ] Statistiques calculées correctement
- [ ] Import Excel fonctionne
- [ ] Emails envoyés correctement

---

## 🎉 Félicitations !

Si tous les tests passent, votre système à 5 comptes est opérationnel !

**Prochaines étapes suggérées :**
1. Créer les templates HTML manquants
2. Améliorer l'interface utilisateur
3. Ajouter des graphiques pour les statistiques
4. Implémenter l'export PDF/Excel
5. Ajouter des notifications en temps réel

---

**Document créé le : 3 Décembre 2024**
**Version : 1.0**

Pour toute question ou problème, consultez la documentation ou contactez le support technique.
