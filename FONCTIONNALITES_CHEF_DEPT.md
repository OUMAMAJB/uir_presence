# ✅ Fonctionnalités Chef de Département - Complètes

## Date: 3 Décembre 2024 - 13h15

---

## 🎯 Vue d'Ensemble

Le **Chef de Département** possède maintenant **TOUTES** les fonctionnalités d'un enseignant en plus de ses fonctions administratives.

---

## ✅ FONCTIONNALITÉS ADMINISTRATIVES

### 1. Gestion des Filières
- ✅ **Créer une filière** (`/department/track/create`)
- ✅ **Modifier une filière** (`/department/track/<id>/edit`)
- ✅ **Supprimer une filière** (`/department/track/<id>/delete`)
  - Vérification : pas d'étudiants inscrits
  - Vérification : pas de matières associées

### 2. Gestion des Chefs de Filière
- ✅ **Nommer un chef de filière** (`/department/track/<id>/assign-head`)
  - Interface GET pour sélectionner l'enseignant
  - Liste des enseignants du même département
  - **Règle importante** : L'ancien chef redevient automatiquement "Enseignant Titulaire"
  
```python
# Gérer l'ancien chef (le remettre enseignant titulaire)
if track.head_id:
    old_head = User.query.get(track.head_id)
    if old_head:
        teacher_role = Role.query.filter_by(name='enseignant').first()
        old_head.role = teacher_role
        flash(f'{old_head.first_name} {old_head.last_name} est redevenu enseignant titulaire.', 'info')
```

### 3. Affectation des Enseignants aux Filières
- ✅ **Affecter des enseignants aux filières** (`/department/teacher/<id>/assign-tracks`)
- ✅ Un enseignant peut enseigner dans **une ou plusieurs filières**
- ✅ Interface avec checkboxes multiples

### 4. Consultation des Étudiants
- ✅ **Liste des étudiants** (`/department/students`)
- ✅ Filtre par filière
- ✅ Vue de tous les étudiants du département

---

## ✅ FONCTIONNALITÉS ENSEIGNANT (NOUVELLES)

### 1. Page "Cours" avec Filtres
**Route** : `/department/courses`

**Filtres disponibles** :
- ✅ Par **filière**
- ✅ Par **année académique**
- ✅ Par **semestre**

**Affichage** :
- Liste des matières filtrées
- Pour chaque matière : nom, filière, semestre
- Lien vers les sessions de la matière

### 2. Gestion des Sessions de Cours
**Route** : `/department/subject/<id>/sessions`

**Filtres disponibles** :
- ✅ Par **date**
- ✅ Par **type** (CM, TD, TP)

**Actions disponibles** :
- ✅ **Créer une session** (`/department/session/create/<subject_id>`)
  - Choisir le type (CM, TD, TP)
  - Choisir la date
  - Choisir l'heure de début et de fin
  
- ✅ **Modifier une session** (`/department/session/<id>/edit`)
  - Modifier tous les champs
  
- ✅ **Supprimer une session** (`/department/session/<id>/delete`)
  - Confirmation requise

### 3. Démarrage de Session avec QR Code
**Route** : `/department/session/<id>/qr`

**Fonctionnalités** :
- ✅ **Bouton "Démarrer"** → Génère le QR code
- ✅ **QR code dynamique** qui se rafraîchit toutes les 15 secondes
- ✅ **Token unique** généré à chaque rafraîchissement
- ✅ **Compteur de présences** en temps réel
- ✅ **Bouton "Arrêter"** → Désactive le QR code

**API Endpoints** :
```python
# Démarrer la session
POST /department/session/<id>/start
→ Génère le token initial et active la session

# Rafraîchir le token (toutes les 15s)
POST /department/session/<id>/refresh_token
→ Génère un nouveau token

# Arrêter la session
POST /department/session/<id>/stop
→ Désactive la session et supprime le token
```

**Code JavaScript** (à implémenter dans le template) :
```javascript
// Rafraîchir le QR code toutes les 15 secondes
setInterval(function() {
    fetch('/department/session/{{ session.id }}/refresh_token', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Mettre à jour le QR code avec le nouveau token
            updateQRCode(data.token);
        }
    });
}, 15000); // 15 secondes
```

### 4. Consultation des Présences
**Route** : `/department/attendances`

**Filtres disponibles** :
- ✅ Par **filière**
- ✅ Par **année** (1ère, 2ème, 3ème, etc.)
- ✅ Par **semestre**
- ✅ Par **matière**
- ✅ Par **type de cours** (CM, TD, TP)
- ✅ Par **date**
- ✅ Par **heure**

**Affichage** :
- Liste complète des présences
- Pour chaque présence :
  - Nom de l'étudiant
  - Matière
  - Type de cours
  - Date et heure
  - Statut (Présent/Absent)
  - Timestamp du scan

### 5. Statistiques du Département
**Route** : `/department/statistics`

**Filtres disponibles** :
- ✅ Par **année académique**
- ✅ Par **semestre**
- ✅ Par **filière**
- ✅ Par **matière**

**Statistiques calculées** :
- Taux de présence global
- Taux de présence par matière
- Taux de présence par filière
- Nombre d'étudiants en rattrapage
- Détails par étudiant

**Règle de Rattrapage** :
```python
# Un étudiant passe en rattrapage si :
# 1. 25% d'absences en CM+TD
if cm_td_absence_percentage >= 25:
    status = 'Rattrapage'

# 2. OU 2 absences en TP
if tp_absences >= 2:
    status = 'Rattrapage'
```

---

## 📋 ROUTES CRÉÉES

### Routes Administratives
1. ✅ `GET/POST /department/dashboard` - Dashboard principal
2. ✅ `GET/POST /department/track/create` - Créer filière
3. ✅ `GET/POST /department/track/<id>/edit` - Modifier filière
4. ✅ `POST /department/track/<id>/delete` - Supprimer filière
5. ✅ `GET/POST /department/track/<id>/assign-head` - Nommer chef filière
6. ✅ `GET/POST /department/teacher/<id>/assign-tracks` - Affecter enseignant
7. ✅ `GET /department/students` - Liste étudiants

### Routes Enseignant (Nouvelles)
8. ✅ `GET /department/courses` - Page cours avec filtres
9. ✅ `GET /department/subject/<id>/sessions` - Sessions d'une matière
10. ✅ `GET/POST /department/session/create/<subject_id>` - Créer session
11. ✅ `GET/POST /department/session/<id>/edit` - Modifier session
12. ✅ `POST /department/session/<id>/delete` - Supprimer session
13. ✅ `POST /department/session/<id>/start` - Démarrer session (API)
14. ✅ `GET /department/session/<id>/qr` - Page QR code
15. ✅ `POST /department/session/<id>/refresh_token` - Rafraîchir QR (API)
16. ✅ `POST /department/session/<id>/stop` - Arrêter session (API)
17. ✅ `GET /department/attendances` - Consultation présences
18. ✅ `GET /department/statistics` - Statistiques département

---

## 🔄 FLUX DE TRAVAIL

### Flux 1: Créer et Démarrer un Cours

1. **Aller sur la page Cours**
   ```
   /department/courses
   ```

2. **Filtrer par filière, année, semestre**
   - Sélectionner les filtres
   - Cliquer "Filtrer"
   - Liste des matières s'affiche

3. **Cliquer sur une matière**
   ```
   /department/subject/<id>/sessions
   ```
   - Voir toutes les sessions de cette matière

4. **Créer une nouvelle session**
   - Cliquer "Créer une session"
   - Choisir le type (CM, TD, TP)
   - Choisir la date et l'heure
   - Cliquer "Créer"

5. **Démarrer la session**
   - Cliquer "Démarrer" sur la session
   - Page QR code s'affiche
   - QR code se rafraîchit toutes les 15s
   - Compteur de présences en temps réel

6. **Arrêter la session**
   - Cliquer "Arrêter"
   - Session désactivée
   - Retour à la liste des sessions

### Flux 2: Consulter les Présences

1. **Aller sur la page Présences**
   ```
   /department/attendances
   ```

2. **Appliquer les filtres**
   - Filière : Génie Informatique
   - Année : 1ère année
   - Semestre : S1
   - Matière : Programmation C
   - Type : CM
   - Date : 2024-12-03

3. **Voir les résultats**
   - Liste de tous les étudiants
   - Statut de chacun (Présent/Absent)
   - Heure du scan pour les présents

### Flux 3: Consulter les Statistiques

1. **Aller sur la page Statistiques**
   ```
   /department/statistics
   ```

2. **Appliquer les filtres**
   - Année : 2024-2025
   - Semestre : S1
   - Filière : Génie Informatique
   - Matière : Programmation C

3. **Voir les statistiques**
   - Taux de présence global
   - Nombre d'étudiants en rattrapage
   - Détails par étudiant

---

## 📝 TEMPLATES À CRÉER

### Templates Administratifs (Déjà créés)
- ✅ `department/dashboard.html`
- ⏳ `department/create_track.html`
- ⏳ `department/edit_track.html`
- ⏳ `department/assign_track_head.html`
- ⏳ `department/assign_teacher_tracks.html`
- ⏳ `department/students.html`

### Templates Enseignant (À créer)
- ⏳ `department/courses.html` - Page cours avec filtres
- ⏳ `department/subject_sessions.html` - Sessions d'une matière
- ⏳ `department/create_session.html` - Créer session
- ⏳ `department/edit_session.html` - Modifier session
- ⏳ `department/session_qr.html` - Page QR code avec rafraîchissement
- ⏳ `department/attendances.html` - Consultation présences
- ⏳ `department/statistics.html` - Statistiques

---

## 🎨 EXEMPLE DE TEMPLATE QR CODE

```html
<!-- department/session_qr.html -->
{% extends "base.html" %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-6">Session en cours</h1>
    
    <div class="bg-white rounded-lg shadow-lg p-8">
        <h2 class="text-2xl font-semibold mb-4">{{ session.subject.name }}</h2>
        <p class="text-gray-600 mb-2">Type: {{ session.type }}</p>
        <p class="text-gray-600 mb-6">Date: {{ session.date.strftime('%d/%m/%Y') }}</p>
        
        <!-- QR Code -->
        <div id="qr-code" class="flex justify-center mb-6">
            <div id="qrcode"></div>
        </div>
        
        <!-- Compteur -->
        <div class="text-center mb-6">
            <p class="text-lg">Étudiants présents: <span id="count" class="font-bold text-green-600">0</span></p>
        </div>
        
        <!-- Bouton Arrêter -->
        <div class="text-center">
            <button onclick="stopSession()" class="bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700">
                Arrêter la session
            </button>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/qrcodejs@1.0.0/qrcode.min.js"></script>
<script>
let currentToken = "{{ session.qr_code_token }}";
let qrcode = null;

// Générer le QR code initial
function generateQRCode(token) {
    document.getElementById('qrcode').innerHTML = '';
    qrcode = new QRCode(document.getElementById("qrcode"), {
        text: token,
        width: 256,
        height: 256
    });
}

// Rafraîchir le QR code toutes les 15 secondes
setInterval(function() {
    fetch('/department/session/{{ session.id }}/refresh_token', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            currentToken = data.token;
            generateQRCode(currentToken);
        }
    });
}, 15000); // 15 secondes

// Mettre à jour le compteur
setInterval(function() {
    fetch('/department/session/{{ session.id }}/count')
    .then(response => response.json())
    .then(data => {
        document.getElementById('count').textContent = data.count;
    });
}, 2000); // 2 secondes

// Arrêter la session
function stopSession() {
    if (confirm('Êtes-vous sûr de vouloir arrêter la session ?')) {
        fetch('/department/session/{{ session.id }}/stop', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = '/department/subject/{{ session.subject_id }}/sessions';
            }
        });
    }
}

// Générer le QR code au chargement
generateQRCode(currentToken);
</script>
{% endblock %}
```

---

## ✅ RÉSUMÉ

Le Chef de Département possède maintenant :

### Fonctionnalités Administratives
- ✅ Gestion complète des filières
- ✅ Nomination des chefs de filière
- ✅ Affectation des enseignants aux filières
- ✅ Consultation des étudiants

### Fonctionnalités Enseignant
- ✅ Page cours avec filtres (filière, année, semestre)
- ✅ Gestion des sessions (créer, modifier, supprimer)
- ✅ Démarrage de session avec QR code dynamique (15s)
- ✅ Consultation des présences avec filtres avancés
- ✅ Statistiques du département avec filtres

### Règles Implémentées
- ✅ Ancien chef de filière → redevient enseignant titulaire
- ✅ QR code se rafraîchit toutes les 15 secondes
- ✅ Rattrapage si 25% absence (CM+TD) ou 2 absences (TP)

---

**Prochaine étape** : Créer les templates HTML pour les nouvelles fonctionnalités !

---

**Document créé le : 3 Décembre 2024 - 13h20**
