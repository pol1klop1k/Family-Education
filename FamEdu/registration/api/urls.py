from django.urls import path
from . import views

urlpatterns = [
    path('auth/me/', views.MeView.as_view()),
    path('schools/', views.SchoolListView.as_view()),
    path('students/', views.StudentsListView.as_view()),
    path('students/<int:pk>/', views.StudentRetrieveView.as_view()),
    path('students/<int:pk>/notifications/', views.NotificationView.as_view()),

    path('trigger-scan/', views.ScanView.as_view()),
    path('extract-data/', views.extract_data_from_doc)
]