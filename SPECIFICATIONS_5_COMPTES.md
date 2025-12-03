# 📋 Spécifications Complètes - Système de Gestion de Présence UIR

## 🎯 Vue d'ensemble

Le système comprend **5 types de comptes** avec une hiérarchie claire et des permissions spécifiques :

1. **Super Chef** (Super Admin)
2. **Chef de Département**
3. **Chef de Filière**
4. **Enseignant Titulaire**
5. **Étudiant**

---

## 👑 1. SUPER CHEF (Super Admin)

### Rôle
Administrateur principal du système avec tous les accès.

### Fonctionnalités

#### 📚 Gestion des Départements
- ✅ Ajouter un département
- ✅ Modifier un département
- ✅ Supprimer un département
- ✅ Consulter la liste des départements

#### 👨‍🏫 Gestion des Enseignants
- ✅ Ajouter un enseignant (manuellement)
- ✅ Importer des enseignants (fichier Excel)
- ✅ Modifier un enseignant
- ✅ Supprimer un enseignant (sélection multiple possible)
- ✅ Consulter la liste des enseignants par département
- ✅ Nommer/Changer le chef de département

#### 🔑 Accès Hérités
Le Super Chef possède **TOUTES** les fonctionnalités des autres administrateurs :
- Toutes les fonctionnalités du Chef de Département
- Toutes les fonctionnalités du Chef de Filière
- Toutes les fonctionnalités de l'Enseignant

---

## 🏢 2. CHEF DE DÉPARTEMENT

### Rôle
Gère un département spécifique et ses filières.

### Fonctionnalités

#### 🎓 Gestion des Filières
- ✅ Ajouter une filière dans son département
- ✅ Modifier une filière
- ✅ Supprimer une filière
- ✅ Consulter la liste des filières

#### 👤 Gestion des Chefs de Filière
- ✅ Nommer un chef de filière
- ✅ Changer un chef de filière
- ⚠️ **Règle importante** : Si un enseignant chef de filière est remplacé, il redevient automatiquement "Enseignant Titulaire"

#### 👥 Affectation des Enseignants
- ✅ Affecter des enseignants aux filières
- ✅ Un enseignant peut enseigner dans **une ou plusieurs filières**
- ✅ Gérer les affectations multiples

#### 👨‍🎓 Consultation des Étudiants
- ✅ Consulter la liste des étudiants inscrits dans chaque filière
- ✅ Filtrer par filière

#### 📖 Fonctionnalités d'Enseignant
Le Chef de Département a **TOUTES** les fonctionnalités d'un enseignant :
- ✅ Créer des cours/séances
- ✅ Démarrer une séance (afficher le QR code qui se rafraîchit toutes les 15s)
- ✅ Modifier une séance
- ✅ Supprimer une séance
- ✅ Consulter l'historique des présences

#### 📊 Statistiques Département
- ✅ Consulter les statistiques de **tout le département**
- ✅ Filtres disponibles :
  - Filière
  - Année
  - Semestre
  - Matière
  - Date et heure
- ✅ Vue globale des présences de tous les étudiants du département

---

## 🎯 3. CHEF DE FILIÈRE

### Rôle
Gère une filière spécifique : structure académique et étudiants.

### Fonctionnalités

#### 📚 Gestion de la Structure Académique
- ✅ Créer les années de formation (1ère année, 2ème année, etc.)
- ✅ Créer les semestres pour chaque année (S1, S2, etc.)
- ✅ Créer les matières pour chaque semestre
- ✅ Pour chaque matière, définir :
  - Nombre de séances CM (Cours Magistraux)
  - Nombre de séances TD (Travaux Dirigés)
  - Nombre de séances TP (Travaux Pratiques)
  - **Calcul automatique** du total de séances

#### 👨‍🏫 Affectation des Enseignants aux Matières
- ✅ Assigner des enseignants à des matières spécifiques
- ✅ Un enseignant ne voit que les matières qui lui sont affectées
- ✅ Gérer les affectations multiples

#### 👨‍🎓 Gestion des Étudiants
- ✅ Ajouter un étudiant (manuellement)
- ✅ Importer des étudiants (fichier Excel)
- ✅ Modifier un étudiant
- ✅ Supprimer un étudiant (sélection multiple possible)
- ✅ Afficher la liste des étudiants avec filtre par année

#### 📖 Fonctionnalités d'Enseignant
Le Chef de Filière a **TOUTES** les fonctionnalités d'un enseignant :
- ✅ Créer des cours/séances
- ✅ Démarrer une séance
- ✅ Modifier une séance
- ✅ Supprimer une séance
- ✅ Consulter l'historique des présences

#### 📊 Statistiques Filière
- ✅ Consulter les statistiques de **toute sa filière**
- ✅ Vue sur toutes les matières de la filière
- ✅ Filtres disponibles :
  - Année
  - Semestre
  - Matière

---

## 👨‍🏫 4. ENSEIGNANT TITULAIRE

### Rôle
Enseigne des matières spécifiques et gère ses cours.

### Fonctionnalités

#### 📖 Gestion des Cours
- ✅ Créer une séance
- ✅ Modifier une séance
- ✅ Supprimer une séance
- ✅ Consulter l'historique des présences de ses séances

#### 🔒 Restrictions d'Accès
- ⚠️ Accès **uniquement** aux matières qui lui sont affectées par le Chef de Filière
- ✅ Peut enseigner **plusieurs matières** dans **plusieurs filières**

#### 🎬 Démarrage de Séance
- ✅ Afficher un **QR code** pour la prise de présence
- ✅ Le QR code se **rafraîchit automatiquement toutes les 15 secondes** (sécurité)
- ✅ **Compteur en temps réel** des étudiants qui ont scanné
- ✅ Les étudiants qui scannent sont marqués **présents**

#### 📋 Historique des Présences
- ✅ Voir les étudiants qui ont scanné → **Présents**
- ✅ Voir les étudiants qui n'ont pas scanné → **Absents**
- ✅ Filtrer par séance

#### 📊 Statistiques
- ✅ Consulter les statistiques pour **ses matières uniquement**
- ✅ Filtres disponibles :
  - Filière
  - Année
  - Matière

### 📐 Règles de Calcul des Statistiques

#### Règle 1 : Marquage Présence/Absence
- ✅ **Présent** : L'étudiant a scanné le QR code pendant la séance active
- ✅ **Absent** : La séance a été démarrée et l'étudiant n'a pas scanné
- ⚠️ **Important** : Si une séance n'a jamais été démarrée, elle **ne compte pas** dans les statistiques

#### Règle 2 : Passage au Rattrapage
Un étudiant passe **automatiquement au rattrapage** si :
- **25% d'absences** sur (CM + TD) pour la matière
- **OU 2 absences** en TP pour la matière

#### Règle 3 : Affichage
- ✅ Afficher le statut de l'étudiant (Admis / Rattrapage)
- ✅ Afficher la note sur 20 (calculée selon les absences)

---

## 👨‍🎓 5. ÉTUDIANT

### Rôle
Participe aux cours et consulte ses présences.

### Fonctionnalités

#### 📱 Scan du QR Code
- ✅ Scanner le QR code affiché par l'enseignant
- ✅ Marquage automatique comme **présent**

#### 🔒 Restrictions de Scan
- ⚠️ **Impossible** de scanner un code d'une autre filière
- ⚠️ **Impossible** de scanner un code d'une autre année
- ✅ Validation automatique de la filière et de l'année

#### 📊 Consultation des Statistiques Personnelles

Pour **chaque matière**, l'étudiant peut consulter :
- ✅ **Nombre total de séances** (démarrées uniquement)
- ✅ **Séances présentes** (où il a scanné)
- ✅ **Séances absentes** (où il n'a pas scanné)
- ✅ **Séances restantes** (non encore effectuées)
- ✅ **Tableau d'historique** détaillé (date, heure, statut)
- ✅ **Son statut** (Admis / Rattrapage)
- ✅ **Pourcentage d'absence**

---

## 🔄 Flux de Connexion

### Redirection Automatique selon le Rôle

Après connexion, l'utilisateur est redirigé vers :

| Rôle | Redirection |
|------|-------------|
| **Super Chef** | `/super-admin/dashboard` |
| **Chef de Département** | `/department/dashboard` |
| **Chef de Filière** | `/track/dashboard` |
| **Enseignant Titulaire** | `/teacher/dashboard` |
| **Étudiant** | `/student/dashboard` |

---

## 🔐 Hiérarchie des Permissions

```
Super Chef (Tous les accès)
    ↓
Chef de Département (Département + Enseignant)
    ↓
Chef de Filière (Filière + Enseignant)
    ↓
Enseignant Titulaire (Ses matières uniquement)
    ↓
Étudiant (Consultation uniquement)
```

---

## 📊 Modèle de Données Requis

### Tables Principales
1. **users** - Tous les utilisateurs
2. **roles** - 5 rôles (super_admin, chef_dept, chef_filiere, enseignant, etudiant)
3. **departments** - Départements
4. **tracks** - Filières
5. **academic_years** - Années de formation
6. **semesters** - Semestres
7. **subjects** - Matières
8. **sessions** - Séances de cours
9. **attendances** - Présences

### Tables d'Association
1. **track_teachers** - Enseignants ↔ Filières (Many-to-Many)
2. **teaching_assignments** - Enseignants ↔ Matières (Many-to-Many)
3. **enrollments** - Étudiants ↔ Matières (Many-to-Many)

---

## 🎨 Fonctionnalités Techniques Clés

### 1. QR Code Dynamique
- ✅ Génération d'un token unique par séance
- ✅ Rafraîchissement automatique toutes les 15 secondes
- ✅ Validation côté serveur (filière, année, timing)

### 2. Import Excel
- ✅ Template Excel fourni
- ✅ Validation des données
- ✅ Création en masse (enseignants et étudiants)

### 3. Calcul Automatique des Statistiques
- ✅ Comptage des présences/absences
- ✅ Calcul du pourcentage
- ✅ Détection automatique du statut Rattrapage
- ✅ Calcul de la note sur 20

### 4. Sélection Multiple
- ✅ Checkboxes pour sélectionner plusieurs enseignants/étudiants
- ✅ Actions groupées (suppression, export)

---

## 📝 Notes Importantes

### Règles de Changement de Rôle
- ⚠️ Un **Chef de Filière** qui est remplacé redevient **Enseignant Titulaire**
- ⚠️ Un **Chef de Département** qui est remplacé redevient **Enseignant Titulaire**

### Règles de Suppression
- ⚠️ Impossible de supprimer un département avec des filières actives
- ⚠️ Impossible de supprimer une filière avec des étudiants inscrits
- ⚠️ Confirmation requise pour toute suppression

### Règles de Sécurité
- ✅ Chaque utilisateur ne voit que ce qui le concerne
- ✅ Validation des permissions à chaque action
- ✅ Logs de toutes les actions administratives

---

**Document créé le : 3 Décembre 2024**
**Version : 1.0**
