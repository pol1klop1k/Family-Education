from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from registration.models import Employee

# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = UserAdmin.fieldsets + (
        ('Employee', {
            'fields': ('name', 'surname', 'patronymic', 'position')
        }),
    )

admin.site.register(User, CustomUserAdmin)