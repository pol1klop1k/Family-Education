from django.urls import path
from . import views

app_name="menu"

urlpatterns = [
    path('', views.MainMenuView.as_view(), name="menu"),
]