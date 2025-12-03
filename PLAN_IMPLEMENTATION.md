# 📋 Plan d'Implémentation - Système 5 Comptes

## 🎯 Objectif
Transformer le système actuel en un système complet avec 5 types de comptes et leurs fonctionnalités spécifiques.

---

## ✅ Phase 1: Mise à Jour des Modèles de Données

### 1.1 Vérifier/Créer les Rôles
- [x] Role: `admin` → Renommer en `super_admin`
- [x] Role: `admin_dept` → Chef de Département
- [x] Role: `admin_filiere` → Chef de Filière  
- [x] Role: `enseignant` → Enseignant Titulaire
- [x] Role: `etudiant` → Étudiant

### 1.2 Ajouter Champs Manquants
- [ ] `User.academic_year` - Année de formation de l'étudiant (1ère, 2ème, etc.)
- [ ] `Session.teacher_id` - Enseignant qui a créé la séance
- [ ] `Session.started_at` - Timestamp de démarrage
- [ ] `Session.stopped_at` - Timestamp d'arrêt

### 1.3 Vérifier Relations Existantes
- [x] `track_teachers` - Enseignants ↔ Filières (Many-to-Many)
- [x] `teaching_assignments` - Enseignants ↔ Matières (Many-to-Many)
- [x] `enrollments` - Étudiants ↔ Matières (Many-to-Many)

---

## ✅ Phase 2: Système d'Authentification et Redirection

### 2.1 Modifier `auth.py`
- [ ] Après login, rediriger selon le rôle :
  - `super_admin` → `/super-admin/dashboard`
  - `admin_dept` → `/department/dashboard`
  - `admin_filiere` → `/track/dashboard`
  - `enseignant` → `/teacher/dashboard`
  - `etudiant` → `/student/dashboard`

### 2.2 Créer Décorateurs de Permission
- [ ] `@super_admin_required`
- [ ] `@dept_admin_required` (inclut super_admin)
- [ ] `@track_admin_required` (inclut super_admin + dept_admin)
- [ ] `@teacher_required` (inclut tous les admins)
- [ ] `@student_required`

---

## ✅ Phase 3: Routes Super Admin

### 3.1 Gestion Départements
- [x] `/super-admin/dashboard` - Vue d'ensemble
- [x] `/super-admin/department/create` - Créer département
- [ ] `/super-admin/department/<id>/edit` - Modifier département
- [ ] `/super-admin/department/<id>/delete` - Supprimer département

### 3.2 Gestion Enseignants
- [x] `/super-admin/teacher/add` - Ajouter enseignant (manuel)
- [ ] `/super-admin/teacher/import` - Importer Excel
- [ ] `/super-admin/teacher/edit/<id>` - Modifier enseignant
- [ ] `/super-admin/teacher/delete` - Supprimer (sélection multiple)
- [x] `/super-admin/teachers/by-department/<id>` - Liste par département

### 3.3 Nomination Chefs
- [x] `/super-admin/department/<id>/assign-head` - Nommer chef département
- [ ] `/super-admin/department/<id>/remove-head` - Retirer chef département

### 3.4 Accès Hérités
- [ ] Accès à toutes les routes de Chef de Département
- [ ] Accès à toutes les routes de Chef de Filière
- [ ] Accès à toutes les routes d'Enseignant

---

## ✅ Phase 4: Routes Chef de Département

### 4.1 Dashboard
- [ ] `/department/dashboard` - Vue d'ensemble du département

### 4.2 Gestion Filières
- [ ] `/department/track/create` - Créer filière
- [ ] `/department/track/<id>/edit` - Modifier filière
- [ ] `/department/track/<id>/delete` - Supprimer filière

### 4.3 Gestion Chefs de Filière
- [ ] `/department/track/<id>/assign-head` - Nommer chef filière
- [ ] `/department/track/<id>/change-head` - Changer chef filière
- [ ] Logique: Ancien chef → redevient enseignant

### 4.4 Affectation Enseignants aux Filières
- [ ] `/department/teacher/<id>/assign-tracks` - Affecter aux filières
- [ ] Un enseignant peut avoir plusieurs filières

### 4.5 Consultation Étudiants
- [ ] `/department/students` - Liste étudiants par filière
- [ ] Filtres: filière

### 4.6 Gestion Cours (Hérité Enseignant)
- [ ] Créer/Modifier/Supprimer séances
- [ ] Démarrer séances avec QR code
- [ ] Consulter historique présences

### 4.7 Statistiques Département
- [ ] `/department/statistics` - Stats globales département
- [ ] Filtres: filière, année, semestre, matière, date

---

## ✅ Phase 5: Routes Chef de Filière

### 5.1 Dashboard
- [ ] `/track/dashboard` - Vue d'ensemble de la filière

### 5.2 Gestion Structure Académique
- [ ] `/track/year/create` - Créer année de formation
- [ ] `/track/year/<id>/semester/create` - Créer semestre
- [ ] `/track/semester/<id>/subject/create` - Créer matière
- [ ] Formulaire matière: CM, TD, TP → Calcul auto total

### 5.3 Affectation Enseignants aux Matières
- [ ] `/track/subject/<id>/assign-teachers` - Affecter enseignants
- [ ] Un enseignant ne voit que ses matières affectées

### 5.4 Gestion Étudiants
- [ ] `/track/student/add` - Ajouter étudiant (manuel)
- [ ] `/track/student/import` - Importer Excel
- [ ] `/track/student/<id>/edit` - Modifier étudiant
- [ ] `/track/student/delete` - Supprimer (sélection multiple)
- [ ] `/track/students` - Liste avec filtre par année

### 5.5 Gestion Cours (Hérité Enseignant)
- [ ] Créer/Modifier/Supprimer séances
- [ ] Démarrer séances avec QR code
- [ ] Consulter historique présences

### 5.6 Statistiques Filière
- [ ] `/track/statistics` - Stats globales filière
- [ ] Filtres: année, semestre, matière

---

## ✅ Phase 6: Routes Enseignant Titulaire

### 6.1 Dashboard
- [x] `/teacher/dashboard` - Ses matières uniquement

### 6.2 Gestion Séances
- [x] `/teacher/session/create/<subject_id>` - Créer séance
- [ ] `/teacher/session/<id>/edit` - Modifier séance
- [ ] `/teacher/session/<id>/delete` - Supprimer séance

### 6.3 Démarrage Séance
- [x] `/teacher/session/<id>/start` - Démarrer (génère QR)
- [x] `/teacher/session/<id>/refresh-token` - Rafraîchir QR (15s)
- [x] `/teacher/session/<id>/stop` - Arrêter séance
- [ ] `/teacher/session/<id>/live` - Vue live avec compteur

### 6.4 Historique Présences
- [ ] `/teacher/session/<id>/attendance` - Historique séance
- [ ] Afficher: Présents (scannés) / Absents (non scannés)

### 6.5 Statistiques
- [ ] `/teacher/statistics` - Ses matières uniquement
- [ ] Filtres: filière, année, matière

---

## ✅ Phase 7: Routes Étudiant

### 7.1 Dashboard
- [ ] `/student/dashboard` - Vue d'ensemble

### 7.2 Scan QR Code
- [ ] `/student/scan` - Interface de scan
- [ ] `/student/scan/submit` - Soumettre scan
- [ ] Validation: filière, année, timing

### 7.3 Consultation Matières
- [ ] `/student/subjects` - Liste de ses matières
- [ ] Pour chaque matière:
  - Total séances (démarrées)
  - Séances présentes
  - Séances absentes
  - Séances restantes
  - Pourcentage absence
  - Statut (Admis / Rattrapage)

### 7.4 Historique Personnel
- [ ] `/student/subject/<id>/history` - Historique matière
- [ ] Tableau: Date, Heure, Type, Statut

---

## ✅ Phase 8: Fonctionnalités Avancées

### 8.1 QR Code Dynamique
- [x] Génération token unique
- [x] Rafraîchissement 15s
- [ ] Affichage compteur temps réel
- [ ] Validation côté serveur

### 8.2 Import Excel
- [ ] Template Excel enseignants
- [ ] Template Excel étudiants
- [ ] Validation données
- [ ] Création en masse

### 8.3 Calcul Statistiques
- [ ] Fonction: Compter présences/absences
- [ ] Fonction: Calculer pourcentage
- [ ] Fonction: Déterminer statut rattrapage
  - 25% absence (CM+TD) → Rattrapage
  - 2 absences TP → Rattrapage
- [ ] Fonction: Calculer note sur 20

### 8.4 Sélection Multiple
- [ ] Checkboxes enseignants
- [ ] Checkboxes étudiants
- [ ] Actions groupées (suppression)

---

## ✅ Phase 9: Templates HTML

### 9.1 Super Admin
- [ ] `super_admin/dashboard.html`
- [ ] `super_admin/manage_departments.html`
- [ ] `super_admin/manage_teachers.html`
- [ ] `super_admin/import_teachers.html`

### 9.2 Chef Département
- [ ] `department/dashboard.html`
- [ ] `department/manage_tracks.html`
- [ ] `department/assign_teachers.html`
- [ ] `department/students.html`
- [ ] `department/statistics.html`

### 9.3 Chef Filière
- [ ] `track/dashboard.html`
- [ ] `track/manage_structure.html`
- [ ] `track/assign_teachers.html`
- [ ] `track/manage_students.html`
- [ ] `track/import_students.html`
- [ ] `track/statistics.html`

### 9.4 Enseignant
- [x] `teacher/dashboard.html`
- [x] `teacher/create_session.html`
- [x] `teacher/qr_code.html`
- [ ] `teacher/session_live.html`
- [ ] `teacher/attendance_history.html`
- [ ] `teacher/statistics.html`

### 9.5 Étudiant
- [ ] `student/dashboard.html`
- [ ] `student/scan_qr.html`
- [ ] `student/subjects.html`
- [ ] `student/subject_history.html`

---

## ✅ Phase 10: Migrations Base de Données

### 10.1 Créer Migrations
- [ ] Ajouter champs manquants
- [ ] Créer/Vérifier rôles
- [ ] Créer données de test

### 10.2 Script de Migration
- [ ] `migrate_to_5_accounts.py`
- [ ] Backup automatique
- [ ] Rollback si erreur

---

## ✅ Phase 11: Tests et Validation

### 11.1 Tests Unitaires
- [ ] Test permissions par rôle
- [ ] Test calcul statistiques
- [ ] Test validation QR code

### 11.2 Tests d'Intégration
- [ ] Test flux complet Super Admin
- [ ] Test flux complet Chef Département
- [ ] Test flux complet Chef Filière
- [ ] Test flux complet Enseignant
- [ ] Test flux complet Étudiant

### 11.3 Tests de Sécurité
- [ ] Impossible d'accéder aux routes non autorisées
- [ ] Validation des données d'entrée
- [ ] Protection CSRF

---

## 📊 Ordre d'Implémentation Recommandé

1. **Phase 1** - Modèles (1-2h)
2. **Phase 2** - Auth & Redirections (1h)
3. **Phase 3** - Super Admin (2-3h)
4. **Phase 6** - Enseignant (2-3h) - Base pour les autres
5. **Phase 7** - Étudiant (2h)
6. **Phase 5** - Chef Filière (3-4h)
7. **Phase 4** - Chef Département (3-4h)
8. **Phase 8** - Fonctionnalités avancées (4-5h)
9. **Phase 9** - Templates (4-6h)
10. **Phase 10** - Migrations (1-2h)
11. **Phase 11** - Tests (2-3h)

**Temps total estimé: 25-35 heures**

---

## 🚀 Prochaines Étapes Immédiates

1. ✅ Créer ce document de planification
2. Mettre à jour `models.py` avec champs manquants
3. Créer script de migration des rôles
4. Mettre à jour `auth.py` avec redirections
5. Créer décorateurs de permissions
6. Commencer par les routes Enseignant (base)
7. Puis routes Étudiant
8. Puis routes Chef Filière
9. Puis routes Chef Département
10. Finaliser Super Admin

---

**Document créé le: 3 Décembre 2024**
**Statut: En cours**
