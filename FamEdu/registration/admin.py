from django.contrib import admin
from .models import Child, Parent, School, Notification


# Register your models here.
admin.site.register(Child)
admin.site.register(Parent)
admin.site.register(School)
admin.site.register(Notification)