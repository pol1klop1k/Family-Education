from django.urls import path
from . import views

urlpatterns = [
    path('', views.RegistrationWizardView.as_view()),
]