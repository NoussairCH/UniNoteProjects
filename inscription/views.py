from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Inscription, ModuleChoisi, Note
from catalogue.models import CatalogueModule, CategorieEvaluation
from accounts.models import Profile
from django.contrib.auth.models import User
import json
from decimal import Decimal


def get_or_create_inscription(user):
    inscription, _ = Inscription.objects.get_or_create(
        etudiant=user,
        annee_academique='2025-2026'
    )
    return inscription


def calcul_modules_data(inscription):
    """Helper : calcule les données de modules + moyennes pour une inscription."""
    modules_data = []
    somme_ponderee = Decimal('0')
    for mc in inscription.modules_choisis.select_related('module_catalogue').prefetch_related(
        'notes__categorie', 'module_catalogue__categories'
    ):
        categories = list(mc.module_catalogue.categories.all())
        notes_map = {n.categorie_id: n for n in mc.notes.all()}
        toutes_saisies = bool(categories) and all(cat.id in notes_map for cat in categories)
        moyenne_module = None
        if toutes_saisies:
            moyenne_module = round(sum(
                float(notes_map[cat.id].valeur) * float(cat.poids) / 100
                for cat in categories
            ), 2)
            somme_ponderee += Decimal(str(moyenne_module)) * mc.module_catalogue.coefficient
        modules_data.append({
            'mc': mc,
            'categories': categories,
            'notes_map': notes_map,
            'toutes_saisies': toutes_saisies,
            'moyenne_module': moyenne_module,
        })
    moyenne_generale = None
    if inscription.est_verrouillee:
        moyenne_generale = round(float(somme_ponderee) / 60, 2)
    return modules_data, moyenne_generale


@login_required
def dashboard(request):
    profile = request.user.profile

    if profile.is_tuteur:
        parraines = User.objects.filter(profile__tuteur=request.user)
        return render(request, 'inscription/tuteur_dashboard.html', {'parraines': parraines})

    # Étudiant : consultation uniquement
    inscription = get_or_create_inscription(request.user)
    modules_data, moyenne_generale = calcul_modules_data(inscription)

    return render(request, 'inscription/dashboard.html', {
        'inscription': inscription,
        'modules_data': modules_data,
        'total_coeff': inscription.total_coefficients(),
        'moyenne_generale': moyenne_generale,
    })


@login_required
def ajouter_module(request, module_id):
    if not request.user.profile.is_etudiant:
        messages.error(request, "Accès refusé.")
        return redirect('catalogue')

    inscription = get_or_create_inscription(request.user)

    if inscription.est_verrouillee:
        messages.error(request, "Votre inscription est verrouillée. Aucune modification n'est possible.")
        return redirect('catalogue')

    module = get_object_or_404(CatalogueModule, id=module_id, est_actif=True)
    total_actuel = inscription.total_coefficients()
    nouveau_total = total_actuel + module.coefficient

    if nouveau_total > 60:
        messages.error(
            request,
            f"Impossible d'ajouter le module « {module.intitule} » (coefficient : {module.coefficient}). "
            f"Votre total actuel est de {total_actuel} points. "
            f"L'ajout porterait le total à {nouveau_total} points, ce qui dépasse la limite de 60."
        )
        return redirect('catalogue')

    if ModuleChoisi.objects.filter(inscription=inscription, module_catalogue=module).exists():
        messages.warning(request, f"Le module « {module.intitule} » est déjà dans votre panier.")
        return redirect('catalogue')

    ModuleChoisi.objects.create(inscription=inscription, module_catalogue=module)
    inscription.verifier_verrouillage()

    if inscription.est_verrouillee:
        messages.success(request, f"Module « {module.intitule} » ajouté. 🎉 Votre inscription est maintenant verrouillée.")
    else:
        messages.success(request, f"Module « {module.intitule} » ajouté au panier.")
    return redirect('catalogue')


@login_required
def retirer_module(request, module_id):
    if not request.user.profile.is_etudiant:
        messages.error(request, "Accès refusé.")
        return redirect('catalogue')

    inscription = get_or_create_inscription(request.user)

    if inscription.est_verrouillee:
        messages.error(request, "Votre inscription est verrouillée. Aucune modification n'est possible.")
        return redirect('catalogue')

    mc = get_object_or_404(ModuleChoisi, inscription=inscription, module_catalogue_id=module_id)
    nom = mc.module_catalogue.intitule
    mc.delete()
    messages.success(request, f"Module « {nom} » retiré du panier.")
    return redirect('catalogue')


# ─── SAISIE DES NOTES : TUTEUR UNIQUEMENT ───────────────────────────────────

@login_required
def tuteur_dashboard(request):
    if not request.user.profile.is_tuteur:
        messages.error(request, "Accès refusé.")
        return redirect('dashboard')
    parraines = User.objects.filter(profile__tuteur=request.user)
    return render(request, 'inscription/tuteur_dashboard.html', {'parraines': parraines})


@login_required
def etudiant_detail_tuteur(request, etudiant_id):
    """Dashboard d'un étudiant vu par son tuteur — avec saisie des notes."""
    if not request.user.profile.is_tuteur:
        messages.error(request, "Accès refusé.")
        return redirect('dashboard')

    etudiant = get_object_or_404(User, id=etudiant_id, profile__tuteur=request.user)
    try:
        inscription = Inscription.objects.get(etudiant=etudiant, annee_academique='2025-2026')
    except Inscription.DoesNotExist:
        inscription = None

    modules_data, moyenne_generale = calcul_modules_data(inscription) if inscription else ([], None)

    return render(request, 'inscription/etudiant_detail_tuteur.html', {
        'etudiant': etudiant,
        'inscription': inscription,
        'modules_data': modules_data,
        'moyenne_generale': moyenne_generale,
    })


@login_required
def saisir_notes(request, mc_id):
    """Saisie des notes par le tuteur pour un module d'un étudiant parrainé."""
    if not request.user.profile.is_tuteur:
        messages.error(request, "Seul le tuteur peut saisir les notes.")
        return redirect('dashboard')

    mc = get_object_or_404(ModuleChoisi, id=mc_id)

    # Vérifier que l'étudiant est bien parrainé par ce tuteur
    if mc.inscription.etudiant.profile.tuteur != request.user:
        messages.error(request, "Vous n'êtes pas le tuteur de cet étudiant.")
        return redirect('dashboard')

    if not mc.inscription.est_verrouillee:
        messages.error(request, "L'inscription de cet étudiant n'est pas encore verrouillée.")
        return redirect('etudiant_detail_tuteur', etudiant_id=mc.inscription.etudiant.id)

    categories = mc.module_catalogue.categories.all()
    notes_existantes = {n.categorie_id: n for n in mc.notes.all()}
    categories_disponibles = [cat for cat in categories if cat.id not in notes_existantes]

    if request.method == 'POST':
        erreurs = []
        for cat in categories_disponibles:
            valeur_str = request.POST.get(f'note_{cat.id}', '').strip()
            if not valeur_str:
                continue
            try:
                valeur = Decimal(valeur_str)
            except Exception:
                erreurs.append(f"Valeur invalide pour « {cat.nom} ».")
                continue
            if valeur < 0 or valeur > 20:
                erreurs.append(f"La note pour « {cat.nom} » doit être comprise entre 0 et 20.")
                continue
            if Note.objects.filter(module_choisi=mc, categorie=cat).exists():
                erreurs.append(f"Une note existe déjà pour « {cat.nom} ».")
                continue
            Note.objects.create(module_choisi=mc, categorie=cat, valeur=valeur)

        if erreurs:
            for e in erreurs:
                messages.error(request, e)
        else:
            messages.success(request, "Notes enregistrées avec succès.")
        return redirect('etudiant_detail_tuteur', etudiant_id=mc.inscription.etudiant.id)

    return render(request, 'inscription/saisir_notes.html', {
        'mc': mc,
        'etudiant': mc.inscription.etudiant,
        'categories': categories,
        'categories_disponibles': categories_disponibles,
        'notes_existantes': notes_existantes,
    })


# ─── COURBE D'ÉVOLUTION ──────────────────────────────────────────────────────

@login_required
def courbe_evolution(request, etudiant_id=None):
    profile = request.user.profile

    if profile.is_tuteur:
        if etudiant_id is None:
            return redirect('dashboard')
        etudiant = get_object_or_404(User, id=etudiant_id, profile__tuteur=request.user)
    else:
        etudiant = request.user

    try:
        inscription = Inscription.objects.get(etudiant=etudiant, annee_academique='2025-2026')
    except Inscription.DoesNotExist:
        return redirect('dashboard')

    toutes_notes = Note.objects.filter(
        module_choisi__inscription=inscription
    ).order_by('date_saisie').select_related('categorie', 'module_choisi__module_catalogue')

    if not toutes_notes:
        return render(request, 'inscription/courbe.html', {
            'labels': '[]', 'data': '[]', 'etudiant': etudiant
        })

    dates_uniques = list(dict.fromkeys(n.date_saisie.date() for n in toutes_notes))
    labels, data = [], []

    for date_d in dates_uniques:
        notes_subset = [n for n in toutes_notes if n.date_saisie.date() <= date_d]
        mc_notes = {}
        for n in notes_subset:
            mid = n.module_choisi_id
            if mid not in mc_notes:
                mc_notes[mid] = {'mc': n.module_choisi, 'notes': {}}
            mc_notes[mid]['notes'][n.categorie_id] = n

        somme = Decimal('0')
        for mid, mc_data in mc_notes.items():
            mc_obj = mc_data['mc']
            cats = list(mc_obj.module_catalogue.categories.all())
            if cats and all(cat.id in mc_data['notes'] for cat in cats):
                moy = sum(
                    float(mc_data['notes'][cat.id].valeur) * float(cat.poids) / 100
                    for cat in cats
                )
                somme += Decimal(str(moy)) * mc_obj.module_catalogue.coefficient

        labels.append(str(date_d))
        data.append(round(float(somme) / 60, 2))

    return render(request, 'inscription/courbe.html', {
        'labels': json.dumps(labels),
        'data': json.dumps(data),
        'etudiant': etudiant,
    })
