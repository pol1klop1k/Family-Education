from django.urls import path
from . import views

urlpatterns = [
    path('auth/me/', views.MeView.as_view()),
    path('schools/', views.SchoolListView.as_view()),
    path('students/', views.StudentsListView.as_view()),
    path('students/<int:pk>/', views.StudentRetrieveView.as_view()),
    path('students/<int:pk>/notifications/', views.NotificationView.as_view()),
    path('students/<int:pk>/documents/', views.UploadScanView.as_view()),
    path('documents/', views.DocumentsListView.as_view()),
    path('notifications/<int:pk>/', views.UpdateNotificationView.as_view()),
    path('notifications/', views.NotificationCreateView.as_view()),

    path('accounting/', views.AccountingView.as_view()),
    path('accounting/<int:pk>/', views.AccountingUpdateView.as_view()),

    path('trigger-scan/', views.ScanView.as_view()),
    path('extract-data/', views.extract_data_from_doc),
    # path('extract-data/', views.mock_extract_data),

    path('auth/login/', views.LoginView.as_view()),
]