from django.shortcuts import render
from django.views.generic.base import TemplateView

# Create your views here.
class MainMenuView(TemplateView):
    template_name = "menu/index.html"
    