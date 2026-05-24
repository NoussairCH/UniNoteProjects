from django.contrib import admin
from .models import Inscription, ModuleChoisi, Note

@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = ['etudiant', 'annee_academique', 'statut']

@admin.register(ModuleChoisi)
class ModuleChoisAdmin(admin.ModelAdmin):
    list_display = ['inscription', 'module_catalogue']

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['module_choisi', 'categorie', 'valeur', 'date_saisie']
