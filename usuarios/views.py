from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView

class EntrarView(LoginView):
   template_name = 'usuarios/login.html'

