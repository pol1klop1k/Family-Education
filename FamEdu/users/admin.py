from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = UserAdmin.fieldsets + (
        ('Employee', {
            'fields': ('name', 'surname', 'patronymic', 'position')
        }),
    )

admin.site.register(User, CustomUserAdmin)