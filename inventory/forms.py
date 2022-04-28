from django import forms
from django.contrib.auth import get_user_model
from inventory.models import *
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.views.generic import UpdateView
from django.db import models
# from django_countries.fields import CountryField
# from constance.admin import ConstanceAdmin, ConstanceForm, Config
# from djmoney.forms.widgets import MoneyWidget
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import Group, User

class AddItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = (
            'item_name','barcode','image','price','discount_price', 'category', 'item_description', 'slug', 'active', 'unit','quantity_at_hand', 'reorder_level')
        widgets = {
            'description': forms.TextInput(attrs={'class': 'js-max-length form-control','max-length': '70', 'id': 'example-max-length4','placeholder': '50 chars limit..', 'data-always-show': 'True',
                                                  'data-pre-text': 'Used', 'data-separator': 'of',
                                                  'data-post-text': 'characters'})
        }

class AddSupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ('name','address','phone_number','description')
        widgets = {
                'phone_number': forms.TextInput(attrs={'class': 'js-max-length form-control', 'id':'phone_number'})
                }


class AddCategoryForm(forms.ModelForm):
    class Meta:
        model = ItemCategory
        fields = ('category_name', 'category_description','category_colour' )
    
class AddUnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ('unit_short_name', 'unit_description', )
    
class AddStockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ('item', 'batch', 'supplier_name','ordered_price','stock_in','unit_quantity')

