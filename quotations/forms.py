from django import forms
from django.contrib.auth import get_user_model
from pos.models import CustomUser, Customer, Item, Order
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.views.generic import UpdateView
from django.db import models
from django_countries.fields import CountryField
from constance.admin import ConstanceAdmin, ConstanceForm, Config
from djmoney.forms.widgets import MoneyWidget
from django.contrib.auth import authenticate, login, logout, get_user_model

from quotations.models import Quotation


class UpdateQuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = ('code', 'status','customer',)
        widgets = {
                'code':forms.TextInput(attrs={'class': 'form-control','readonly':'readonly'}),
                }