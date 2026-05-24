# UniNotes ERP

> Application web de suivi académique — Mini-projet universitaire Django  
> Esprit School of Engineering — Mai 2026

---

## Présentation du projet

**UniNotes ERP** est une application web de suivi académique développée avec le framework Django. Elle permet à chaque étudiant de **composer librement son année académique** en sélectionnant des modules dans un catalogue, sous la contrainte stricte de **60 points de coefficient**, puis de saisir ses notes et de suivre son évolution via un tableau de bord personnalisé.

### Fonctionnalités principales

- **Gestion des comptes** : inscription, connexion, déconnexion avec différenciation des rôles Étudiant / Tuteur
- **Catalogue de modules** : consultation avec coefficients et catégories d'évaluation
- **Panier d'inscription** : sélection libre avec contrainte des 60 points et verrouillage automatique
- **Moteur de suggestions** : recommandation des modules compatibles avec les points restants
- **Saisie des notes** : par catégories d'évaluation avec pondérations, saisie progressive
- **Calcul des moyennes** : moyenne pondérée par module et moyenne générale via ORM Django
- **Courbe d'évolution** : reconstitution historique de la moyenne générale (Chart.js)
- **Dashboard tuteur** : accès en lecture seule aux dashboards des étudiants parrainés

---

## Instructions d'installation

### Prérequis

- Python 3.10+
- pip

### Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/votre_username/uninotes_erp_prenom_nom.git
cd uninotes_erp_prenom_nom

# 2. Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Appliquer les migrations
python manage.py migrate

# 5. (Optionnel) Peupler avec les données de test
python seed_data.py

# 6. Lancer le serveur
python manage.py runserver
```

L'application est accessible à l'adresse : **http://127.0.0.1:8000/**

### Comptes de test disponibles (après seed_data.py)

| Nom d'utilisateur | Mot de passe | Rôle | État |
|---|---|---|---|
| `admin` | `admin1234` | Superuser | — |
| `tuteur1` | `tuteur1234` | Tuteur | Parraine les 3 étudiants |
| `ali_ben_ali` | `etudiant1234` | Étudiant | Inscription verrouillée + notes saisies |
| `sarra_mrad` | `etudiant1234` | Étudiant | Inscription verrouillée, notes partielles |
| `omar_triki` | `etudiant1234` | Étudiant | Panier ouvert (non verrouillé) |

---

## Structure du projet

```
uninotes_erp/
│
├── uninotes_erp/          # Configuration Django (settings, urls, wsgi)
│   ├── settings.py
│   └── urls.py
│
├── accounts/              # App : gestion des utilisateurs et rôles
│   ├── models.py          # Modèle Profile (OneToOne avec User)
│   ├── forms.py           # Formulaire d'inscription avec sélection de rôle
│   ├── views.py           # Inscription, login, logout
│   └── urls.py
│
├── catalogue/             # App : référentiel des modules
│   ├── models.py          # CatalogueModule, CategorieEvaluation
│   ├── views.py           # Vue catalogue avec panier et suggestions
│   └── urls.py
│
├── inscription/           # App : inscription, notes, dashboard
│   ├── models.py          # Inscription, ModuleChoisi, Note
│   ├── views.py           # Dashboard, ajout/retrait modules, saisie notes, courbe
│   ├── urls.py
│   └── templatetags/
│       └── inscription_tags.py   # Filtre dict_get pour les templates
│
├── templates/             # Templates HTML globaux
│   ├── base.html          # Template de base avec navbar
│   ├── accounts/
│   ├── catalogue/
│   └── inscription/
│
├── static/css/
│   └── style.css          # Feuille de style complète (variables CSS, composants)
│
├── seed_data.py           # Script de peuplement des données de test
├── db_export.sql          # Export SQL de la base avec données de test
├── db.sqlite3             # Base de données SQLite
└── requirements.txt
```

---

## Choix techniques et décisions d'architecture

### 1. Séparation Référentiel / Choix utilisateur

Le modèle de données est architecturé autour d'une séparation stricte entre :
- **Le référentiel** (`CatalogueModule`, `CategorieEvaluation`) : données stables gérées par l'administrateur
- **Les données utilisateur** (`Inscription`, `ModuleChoisi`, `Note`) : décisions propres à chaque étudiant

Cette séparation garantit que la suppression ou la modification d'un module du catalogue n'impacte pas les données existantes des étudiants (stratégie `on_delete=PROTECT` sur les clés étrangères).

### 2. Contrainte des 60 points

La contrainte est vérifiée **côté serveur** dans la vue `ajouter_module` avant toute insertion en base. Le verrouillage automatique (`verifier_verrouillage()`) est appelé après chaque ajout réussi et compare le total des coefficients à 60 via une requête ORM agrégée (`Sum`).

### 3. Calcul des moyennes via ORM

Conformément aux exigences pédagogiques, les calculs de moyennes utilisent les capacités d'agrégation de l'ORM Django :
- `Sum()`, `F()`, `ExpressionWrapper()` pour les agrégations
- Les calculs sont réalisés en base de données, pas en boucle Python pure
- La moyenne générale divisée toujours par 60 (même si certains modules n'ont pas encore toutes leurs notes)

### 4. Courbe d'évolution (reconstitution historique)

La courbe est construite par reconstitution historique : pour chaque date de saisie `D`, on filtre les notes dont `date_saisie <= D` et on recalcule la moyenne générale sur ce sous-ensemble. Les dates sont triées chronologiquement et les données sont passées au template en JSON pour Chart.js.

### 5. Isolation des données

L'isolation est implémentée **au niveau des vues** (et non seulement des templates) : chaque requête de données filtre systématiquement par `etudiant=request.user`. Le rôle tuteur donne accès en lecture seule uniquement aux étudiants liés via la relation de parrainage.

### 6. Intégrité référentielle — stratégie choisie

Stratégie retenue : **protection par contrainte de clé étrangère** (`on_delete=PROTECT`).  
Si un administrateur tente de supprimer un module du catalogue déjà sélectionné par des étudiants (`ModuleChoisi`), Django lèvera une `ProtectedError` et refusera la suppression. L'alternative (archivage avec champ `est_actif`) est implémentée en complément : un module peut être désactivé (`est_actif=False`) pour le retirer du catalogue visible sans supprimer les données existantes.

---

## Limites connues et perspectives d'amélioration

### Limites actuelles

- La courbe d'évolution utilise une boucle Python pour la dimension temporelle (inévitable pour la logique de reconstitution historique ; les calculs de moyennes à l'intérieur de la boucle utilisent bien l'ORM)
- Le moteur de recommandation est purement déterministe (filtre sur coefficient ≤ reste) ; pas d'apprentissage ni de personnalisation avancée
- Pas de pagination sur le catalogue pour les très grands nombres de modules
- L'assignation tuteur/étudiant se fait uniquement via l'interface d'administration

### Améliorations envisageables

- Pagination AJAX du catalogue et mises à jour du panier sans rechargement de page
- Export PDF des résultats académiques
- Système de notifications (email) lors du verrouillage de l'inscription
- Gestion multi-année académique avec historique des inscriptions
- Tableau de bord analytique pour le tuteur (comparaison entre étudiants)
- Tests unitaires et d'intégration (Django TestCase, pytest-django)
- Déploiement sur serveur de production (Gunicorn + Nginx + PostgreSQL)
