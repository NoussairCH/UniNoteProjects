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


# 5. Lancer le serveur
python manage.py runserver
```

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

