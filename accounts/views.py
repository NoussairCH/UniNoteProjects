from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from .forms import InscriptionForm

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Bienvenue {user.first_name} ! Votre compte a été créé.")
            return redirect('dashboard')
    else:
        form = InscriptionForm()
    return render(request, 'accounts/register.html', {'form': form})
