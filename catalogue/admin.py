from django.contrib import admin
from .models import CatalogueModule, CategorieEvaluation

class CategorieInline(admin.TabularInline):
    model = CategorieEvaluation
    extra = 1

@admin.register(CatalogueModule)
class CatalogueModuleAdmin(admin.ModelAdmin):
    list_display = ['intitule', 'coefficient', 'est_actif']
    inlines = [CategorieInline]

@admin.register(CategorieEvaluation)
class CategorieEvaluationAdmin(admin.ModelAdmin):
    list_display = ['nom', 'module', 'poids']
