from django.contrib import admin
from django.contrib import admin
from django.contrib.auth import get_user_model
from django import forms

from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from constance.admin import ConstanceAdmin, ConstanceForm, Config

from expenses.models import *


# Register your models here.
CustomUser = get_user_model()

class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'category_description')
    search_fields = ['category_name']

    class Meta:
        model = ExpenseCategory

admin.site.register(ExpenseCategory, ExpenseCategoryAdmin)


class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('batch_number','expense_name', 'expense_description','category','amount','payment_mode')
    search_fields = ['expense_name']

    class Meta:
        model = Expense

admin.site.register(Expense, ExpenseAdmin)


