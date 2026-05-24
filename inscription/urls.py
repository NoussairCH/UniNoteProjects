from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('module/<int:module_id>/ajouter/', views.ajouter_module, name='ajouter_module'),
    path('module/<int:module_id>/retirer/', views.retirer_module, name='retirer_module'),
    path('courbe/', views.courbe_evolution, name='courbe_evolution'),
    # Tuteur
    path('tuteur/etudiant/<int:etudiant_id>/', views.etudiant_detail_tuteur, name='etudiant_detail_tuteur'),
    path('tuteur/etudiant/<int:etudiant_id>/courbe/', views.courbe_evolution, name='courbe_evolution_tuteur'),
    path('tuteur/notes/<int:mc_id>/saisir/', views.saisir_notes, name='saisir_notes'),
]
