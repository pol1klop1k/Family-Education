from django.contrib import admin

from .models import AccountingList
# Register your models here.


@admin.register(AccountingList)
class AccountingList(admin.ModelAdmin):
    pass
