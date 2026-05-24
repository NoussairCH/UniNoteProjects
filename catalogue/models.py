from django.db import models

class CatalogueModule(models.Model):
    intitule = models.CharField(max_length=200, unique=True, verbose_name="Intitulé")
    coefficient = models.PositiveIntegerField(verbose_name="Coefficient")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    est_actif = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Module du catalogue"
        ordering = ['intitule']

    def __str__(self):
        return f"{self.intitule} (coeff. {self.coefficient})"


class CategorieEvaluation(models.Model):
    module = models.ForeignKey(
        CatalogueModule, on_delete=models.PROTECT,
        related_name='categories', verbose_name="Module"
    )
    nom = models.CharField(max_length=100, verbose_name="Nom de la catégorie")
    poids = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Poids (%)")

    class Meta:
        verbose_name = "Catégorie d'évaluation"
        unique_together = [('module', 'nom')]

    def __str__(self):
        return f"{self.nom} ({self.poids}%) - {self.module.intitule}"
