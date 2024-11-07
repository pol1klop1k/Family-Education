from django.urls import path
from . import views

app_name="registration"

urlpatterns = [
    path('new/', views.RegistrationWizardView.as_view(), name="new_notification"),
    path('report/', views.NotificationReportView.as_view(), name="report"),
    path('', views.RegistrationMenuView.as_view(), name="menu"),
]