"""
Script de peuplement de la base de données avec des données de test.
Usage: python manage.py shell < seed_data.py
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uninotes_erp.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Profile
from catalogue.models import CatalogueModule, CategorieEvaluation
from inscription.models import Inscription, ModuleChoisi, Note
from django.utils import timezone
from datetime import timedelta

print("Nettoyage des données existantes...")
Note.objects.all().delete()
ModuleChoisi.objects.all().delete()
Inscription.objects.all().delete()
CategorieEvaluation.objects.all().delete()
CatalogueModule.objects.all().delete()
Profile.objects.all().delete()
User.objects.filter(is_superuser=False).delete()

print("Création du catalogue de modules...")
modules_data = [
    ("Algorithmique et Structures de Données", 10, "Bases de l'algorithmique, complexité, listes, arbres, graphes."),
    ("Programmation Orientée Objet", 8, "Concepts de la POO : classes, héritage, polymorphisme, encapsulation."),
    ("Base de Données Relationnelles", 8, "Modélisation, SQL, normalisation, transactions et optimisation."),
    ("Réseaux et Protocoles", 6, "Modèle OSI/TCP-IP, protocoles, sécurité des réseaux."),
    ("Systèmes d'Exploitation", 6, "Gestion des processus, mémoire, fichiers, Linux."),
    ("Développement Web Front-End", 8, "HTML5, CSS3, JavaScript ES6+, frameworks modernes."),
    ("Développement Web Back-End", 8, "Django, REST API, authentification, déploiement."),
    ("Intelligence Artificielle", 6, "Machine learning, réseaux de neurones, traitement du langage."),
    ("Mathématiques Discrètes", 4, "Logique, ensembles, combinatoire, théorie des graphes."),
    ("Génie Logiciel", 6, "UML, méthodes agiles, tests, CI/CD, qualité du code."),
    ("Sécurité Informatique", 4, "Cryptographie, OWASP, pentesting, cybersécurité."),
    ("Cloud et DevOps", 4, "Docker, Kubernetes, AWS/Azure, pipelines CI/CD."),
]

modules = []
for intitule, coeff, desc in modules_data:
    m = CatalogueModule.objects.create(intitule=intitule, coefficient=coeff, description=desc)
    modules.append(m)
    print(f"  Module créé : {intitule} (coeff {coeff})")

print("Création des catégories d'évaluation...")
cats_config = {
    "Algorithmique et Structures de Données": [("Contrôle Continu", 30), ("Examen Terminal", 50), ("TP", 20)],
    "Programmation Orientée Objet": [("Contrôle Continu", 40), ("Examen Terminal", 60)],
    "Base de Données Relationnelles": [("Contrôle Continu", 30), ("Projet", 30), ("Examen Terminal", 40)],
    "Réseaux et Protocoles": [("Contrôle Continu", 40), ("Examen Terminal", 60)],
    "Systèmes d'Exploitation": [("TP", 40), ("Examen Terminal", 60)],
    "Développement Web Front-End": [("Projet", 60), ("Contrôle Continu", 40)],
    "Développement Web Back-End": [("Projet", 70), ("Contrôle Continu", 30)],
    "Intelligence Artificielle": [("Projet", 50), ("Examen Terminal", 50)],
    "Mathématiques Discrètes": [("Contrôle Continu", 50), ("Examen Terminal", 50)],
    "Génie Logiciel": [("Projet", 60), ("Contrôle Continu", 40)],
    "Sécurité Informatique": [("Contrôle Continu", 50), ("TP", 50)],
    "Cloud et DevOps": [("Projet", 70), ("Contrôle Continu", 30)],
}
for m in modules:
    for nom, poids in cats_config.get(m.intitule, []):
        CategorieEvaluation.objects.create(module=m, nom=nom, poids=poids)

print("Création du tuteur...")
tuteur_user = User.objects.create_user('tuteur1', 'tuteur@esp.tn', 'tuteur1234', first_name='Ahmed', last_name='Ben Salem')
tuteur_profile = Profile.objects.create(user=tuteur_user, role='tuteur')

print("Création des étudiants...")
etudiants_data = [
    ('ali_ben_ali', 'Ali', 'Ben Ali', 'ali@esp.tn'),
    ('sarra_mrad', 'Sarra', 'Mrad', 'sarra@esp.tn'),
    ('omar_triki', 'Omar', 'Triki', 'omar@esp.tn'),
]

etudiants = []
for username, fn, ln, email in etudiants_data:
    u = User.objects.create_user(username, email, 'etudiant1234', first_name=fn, last_name=ln)
    Profile.objects.create(user=u, role='etudiant', tuteur=tuteur_user)
    etudiants.append(u)
    print(f"  Étudiant : {fn} {ln}")

print("Création des inscriptions et paniers...")

def get_module(name):
    return CatalogueModule.objects.get(intitule=name)

# Étudiant 1 : panier verrouillé avec notes
e1 = etudiants[0]
insc1 = Inscription.objects.create(etudiant=e1, annee_academique='2025-2026', statut='verrouillee')
panier1 = [
    "Algorithmique et Structures de Données",  # 10
    "Programmation Orientée Objet",             # 8
    "Base de Données Relationnelles",            # 8
    "Développement Web Front-End",               # 8
    "Développement Web Back-End",                # 8
    "Génie Logiciel",                            # 6
    "Réseaux et Protocoles",                     # 6
    "Systèmes d'Exploitation",                   # 6
]  # total: 60
mcs1 = {}
for nom in panier1:
    mc = ModuleChoisi.objects.create(inscription=insc1, module_catalogue=get_module(nom))
    mcs1[nom] = mc

# Notes pour étudiant 1
notes_data_e1 = {
    "Algorithmique et Structures de Données": {"Contrôle Continu": (14, 0), "Examen Terminal": (12, 1), "TP": (16, 2)},
    "Programmation Orientée Objet": {"Contrôle Continu": (15, 3), "Examen Terminal": (13, 4)},
    "Base de Données Relationnelles": {"Contrôle Continu": (17, 5), "Projet": (16, 6), "Examen Terminal": (14, 7)},
    "Développement Web Front-End": {"Projet": (18, 8), "Contrôle Continu": (15, 9)},
}
base_time = timezone.now() - timedelta(days=30)
for nom_module, cats_notes in notes_data_e1.items():
    mc = mcs1[nom_module]
    for nom_cat, (valeur, delta_days) in cats_notes.items():
        cat = CategorieEvaluation.objects.get(module=mc.module_catalogue, nom=nom_cat)
        n = Note.objects.create(module_choisi=mc, categorie=cat, valeur=valeur)
        # Simulate different dates
        n.date_saisie = base_time + timedelta(days=delta_days*3)
        n.save()

# Étudiant 2 : panier verrouillé, notes partielles
e2 = etudiants[1]
insc2 = Inscription.objects.create(etudiant=e2, annee_academique='2025-2026', statut='verrouillee')
panier2 = [
    "Intelligence Artificielle",   # 6
    "Sécurité Informatique",       # 4
    "Cloud et DevOps",             # 4
    "Mathématiques Discrètes",     # 4
    "Développement Web Back-End",  # 8
    "Base de Données Relationnelles", # 8
    "Algorithmique et Structures de Données", # 10
    "Réseaux et Protocoles",       # 6
    "Systèmes d'Exploitation",     # 6
    "Génie Logiciel",              # 4 → total: 60
]
# Recalculate: 6+4+4+4+8+8+10+6+6+6=62 — fix
panier2 = [
    "Intelligence Artificielle",   # 6
    "Sécurité Informatique",       # 4
    "Cloud et DevOps",             # 4
    "Mathématiques Discrètes",     # 4
    "Développement Web Back-End",  # 8
    "Base de Données Relationnelles", # 8
    "Algorithmique et Structures de Données", # 10
    "Réseaux et Protocoles",       # 6
    "Systèmes d'Exploitation",     # 6
    "Programmation Orientée Objet", # 8
    "Génie Logiciel",              # 6
]
# 6+4+4+4+8+8+10+6+6+8+6=70 — too much. Let's do:
panier2 = [
    "Algorithmique et Structures de Données", # 10
    "Développement Web Front-End",            # 8
    "Développement Web Back-End",             # 8
    "Intelligence Artificielle",              # 6
    "Réseaux et Protocoles",                  # 6
    "Systèmes d'Exploitation",               # 6
    "Sécurité Informatique",                 # 4
    "Cloud et DevOps",                        # 4
    "Mathématiques Discrètes",               # 4
    "Programmation Orientée Objet",          # 8 → total: 10+8+8+6+6+6+4+4+4+8 = 64 — still too much
]
# Fine: 10+8+8+6+6+6+4+4+4 = 56, add Geo Logiciel 6 = 62. Use: 10+8+8+6+6+6+4+4 = 52, add POO 8 = 60
panier2 = [
    "Algorithmique et Structures de Données", # 10
    "Développement Web Front-End",            # 8
    "Développement Web Back-End",             # 8
    "Intelligence Artificielle",              # 6
    "Réseaux et Protocoles",                  # 6
    "Systèmes d'Exploitation",               # 6
    "Sécurité Informatique",                 # 4
    "Cloud et DevOps",                        # 4
    "Programmation Orientée Objet",          # 8 → total: 60 ✓
]
mcs2 = {}
for nom in panier2:
    mc = ModuleChoisi.objects.create(inscription=insc2, module_catalogue=get_module(nom))
    mcs2[nom] = mc
# Partial notes for e2
mc = mcs2["Développement Web Front-End"]
for nom_cat, val in [("Projet", 19), ("Contrôle Continu", 17)]:
    cat = CategorieEvaluation.objects.get(module=mc.module_catalogue, nom=nom_cat)
    Note.objects.create(module_choisi=mc, categorie=cat, valeur=val)

# Étudiant 3 : panier ouvert (non verrouillé)
e3 = etudiants[2]
insc3 = Inscription.objects.create(etudiant=e3, annee_academique='2025-2026', statut='ouverte')
for nom in ["Algorithmique et Structures de Données", "Programmation Orientée Objet", "Mathématiques Discrètes"]:
    ModuleChoisi.objects.create(inscription=insc3, module_catalogue=get_module(nom))

print("Création du superuser admin...")
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@esp.tn', 'admin1234')

print("\n✅ Données de test créées avec succès !")
print("\nComptes disponibles:")
print("  admin / admin1234 (superuser)")
print("  tuteur1 / tuteur1234 (tuteur)")
print("  ali_ben_ali / etudiant1234 (étudiant, inscription verrouillée avec notes)")
print("  sarra_mrad / etudiant1234 (étudiant, inscription verrouillée, notes partielles)")
print("  omar_triki / etudiant1234 (étudiant, panier ouvert)")
