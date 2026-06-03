from django.contrib import admin
from .models import Child, DocumentScan, Parent, School, Notification, Employee
from django.contrib.auth import get_user_model
User = get_user_model()


# Register your models here.


admin.site.register(Child)
admin.site.register(Parent)
admin.site.register(School)
admin.site.register(Notification)
admin.site.register(Employee)
admin.site.register(DocumentScan)