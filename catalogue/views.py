from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import CatalogueModule
from inscription.models import Inscription, ModuleChoisi

@login_required
def catalogue(request):
    profile = request.user.profile
    modules = CatalogueModule.objects.filter(est_actif=True).prefetch_related('categories')
    
    inscription = None
    modules_choisis_ids = []
    total_coeff = 0
    reste = 60

    if profile.is_etudiant:
        try:
            inscription = Inscription.objects.get(etudiant=request.user, annee_academique='2025-2026')
            modules_choisis_ids = list(
                ModuleChoisi.objects.filter(inscription=inscription)
                .values_list('module_catalogue_id', flat=True)
            )
            from django.db.models import Sum
            agg = ModuleChoisi.objects.filter(inscription=inscription).aggregate(
                total=Sum('module_catalogue__coefficient')
            )
            total_coeff = agg['total'] or 0
            reste = 60 - total_coeff
        except Inscription.DoesNotExist:
            pass

    return render(request, 'catalogue/catalogue.html', {
        'modules': modules,
        'inscription': inscription,
        'modules_choisis_ids': modules_choisis_ids,
        'total_coeff': total_coeff,
        'reste': reste,
    })
