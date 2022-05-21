from dataclasses import field, fields
from importlib.metadata import files
from django import forms
from django.contrib.auth import get_user_model
from inventory.models import *
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.views.generic import UpdateView
from django.db import models

from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import Group, User
from .models import *

from bootstrap_datepicker_plus.widgets import DatePickerInput, TimePickerInput, DateTimePickerInput, MonthPickerInput, YearPickerInput

class AddExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = (
            'batch_number','expense_name','category','amount','expense_description','payment_mode','amount','created_at','paid_by')
        widgets = {
            'expense_description': forms.TextInput(attrs={'class': 'js-max-length form-control','max-length': '70', 'id': 'example-max-length4','placeholder': '70 chars limit..', 'data-always-show': 'True',
                                                  'data-pre-text': 'Used', 'data-separator': 'of',
                                                  'data-post-text': 'characters'}),
            'created_at': DateTimePickerInput(),
            'paid_by': forms.TextInput(attrs={'class': 'form-control', 'readonly':'readonly'})
        }

class AddExpenseCategory(forms.ModelForm):
    class Meta:
        fields = ('category_name', 'category_description')
        widgets = {
            'category_description': forms.TextInput(attrs={'class': 'js-max-length form-control','max-length': '70', 'id': 'example-max-length4','placeholder': '50 chars limit..', 'data-always-show': 'True',
                                                  'data-pre-text': 'Used', 'data-separator': 'of',
                                                  'data-post-text': 'characters'}),
        }
