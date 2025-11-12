from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth import get_user_model, authenticate, login, logout

# Create your views here.
class SignInView(TemplateView):
    template_name = 'web/auth/signin.html'

class SignUpView(TemplateView):
    template_name = 'web/auth/signup.html'

class HomeView(TemplateView):
    template_name = 'web/home.html'

class SignOutView(TemplateView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('signin')