from django.urls import path
from . import views

urlpatterns = [
   path('trigger-scan/', views.ScanView.as_view()),
   path('extract-data/', views.extract_data_from_doc)
]