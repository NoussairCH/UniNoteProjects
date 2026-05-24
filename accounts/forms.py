from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class InscriptionForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, label="Prénom")
    last_name = forms.CharField(max_length=50, required=True, label="Nom")
    email = forms.EmailField(required=True, label="Email")
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, widget=forms.RadioSelect, label="Rôle")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            Profile.objects.create(user=user, role=self.cleaned_data['role'])
        return user
