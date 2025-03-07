from django.urls import path, include
from . import views
from . import models

app_name="registration"

directories = [

    path('school/create/', views.SchoolWizardView.as_view(), name="school_create"),
    path('<slug:entity>/', views.DirectoryListView.as_view(), name="directory_list"),
    path('<slug:entity>/create/', views.DirectoryCreateView.as_view(), name="directory_create"),
    path('<slug:entity>/update/<int:pk>/', views.DirectoryUpdateView.as_view(), name="directory_update"),
    path('notification/detail/<int:pk>/', views.DirectoryDetailView.as_view(model=models.Notification, template_name="registration_app/directories/notification_detail.html"), name="notification_detail"),
]

urlpatterns = [
    path('new/', views.RegistrationWizardView.as_view(), name="new_notification"),
    path('report/<slug:report_type>/', views.NotificationReportListView.as_view(), name="report"),
    path('directories/', include(directories)),
    path('', views.RegistrationMenuView.as_view(), name="menu"),
]