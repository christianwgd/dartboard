from django.shortcuts import render, redirect
from django.urls import reverse


def logout_user(request):
    redirect(reverse('home'))


def login_form(request):
    return render(request, 'accounts/login.html', {})
