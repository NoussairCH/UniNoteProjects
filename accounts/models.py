from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_ETUDIANT = 'etudiant'
    ROLE_TUTEUR = 'tuteur'
    ROLE_CHOICES = [
        (ROLE_ETUDIANT, 'Étudiant'),
        (ROLE_TUTEUR, 'Tuteur'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_ETUDIANT)
    tuteur = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='parraines',
        limit_choices_to={'profile__role': 'tuteur'}
    )

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_etudiant(self):
        return self.role == self.ROLE_ETUDIANT

    @property
    def is_tuteur(self):
        return self.role == self.ROLE_TUTEUR
