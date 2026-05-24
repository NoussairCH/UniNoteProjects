from django.db import models
from django.contrib.auth.models import User
from catalogue.models import CatalogueModule, CategorieEvaluation
from django.core.validators import MinValueValidator, MaxValueValidator

class Inscription(models.Model):
    STATUT_OUVERTE = 'ouverte'
    STATUT_VERROUILLEE = 'verrouillee'
    STATUT_CHOICES = [
        (STATUT_OUVERTE, 'Ouverte'),
        (STATUT_VERROUILLEE, 'Verrouillée'),
    ]
    etudiant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inscriptions')
    annee_academique = models.CharField(max_length=9, default='2025-2026')
    statut = models.CharField(max_length=12, choices=STATUT_CHOICES, default=STATUT_OUVERTE)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('etudiant', 'annee_academique')]
        verbose_name = "Inscription"

    def __str__(self):
        return f"{self.etudiant.username} - {self.annee_academique} ({self.statut})"

    @property
    def est_verrouillee(self):
        return self.statut == self.STATUT_VERROUILLEE

    def total_coefficients(self):
        from django.db.models import Sum
        agg = self.modules_choisis.aggregate(total=Sum('module_catalogue__coefficient'))
        return agg['total'] or 0

    def verifier_verrouillage(self):
        if self.total_coefficients() == 60:
            self.statut = self.STATUT_VERROUILLEE
            self.save()


class ModuleChoisi(models.Model):
    inscription = models.ForeignKey(Inscription, on_delete=models.CASCADE, related_name='modules_choisis')
    module_catalogue = models.ForeignKey(CatalogueModule, on_delete=models.PROTECT, related_name='modules_choisis')

    class Meta:
        unique_together = [('inscription', 'module_catalogue')]
        verbose_name = "Module choisi"

    def __str__(self):
        return f"{self.inscription.etudiant.username} → {self.module_catalogue.intitule}"


class Note(models.Model):
    module_choisi = models.ForeignKey(ModuleChoisi, on_delete=models.CASCADE, related_name='notes')
    categorie = models.ForeignKey(CategorieEvaluation, on_delete=models.CASCADE, related_name='notes')
    valeur = models.DecimalField(
        max_digits=4, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(20)]
    )
    date_saisie = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('module_choisi', 'categorie')]
        verbose_name = "Note"
        ordering = ['date_saisie']

    def __str__(self):
        return f"{self.module_choisi} - {self.categorie.nom}: {self.valeur}"
