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
    
class UserAdminCreationForm(forms.ModelForm):
    # a form for creating new users. Includes all the required fields
    #plus a repeated password
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password Confirmation', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('email','full_name','image','phone_number','active', 'admin','staff','superuser','user_role')
        widgets = {
                'phone_number': forms.TextInput(attrs={'class': 'js-max-length form-control payment_form', 'id':'phone_number'})
                }
    def clean_password2(self):
        #check that the 2 password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't Match!")
        return password2
    def save(self, commit = True):
        # save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class EditUserPermissionsForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('email','full_name','phone_number','user_role','image','active', 'admin','staff','superuser')
        widgets = {
                'email':forms.TextInput(attrs={'class': 'form-control','readonly':'readonly'}),
                'full_name':forms.TextInput(attrs={'class': 'form-control','readonly':'readonly'}),
                'phone_number': forms.TextInput(attrs={'class': 'js-max-length form-control payment_form', 'id':'phone_number'})
                }
        
        def save(self, commit = True):
            user = super(EditUserPermissionsForm, self).save(commit=False)
            if commit:
                user.save()
            return user

class ChangeUserPasswordForm(forms.ModelForm):
    # a form for creating new users. Includes all the required fields
    #plus a repeated password
    old_password = forms.CharField(label = 'Current Password', widget = forms.PasswordInput)
    password1 = forms.CharField(label='New Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm New Password', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('email',)
        widgets = {
                'email':forms.TextInput(attrs={'class': 'form-control','readonly':'readonly'}),
                }

    def clean_password(self):
        old_password = self.cleaned_data.get("old_password")
        user_password = CustomUser.password
        if CustomUser.check_password(old_password, user_password ) != True:
            raise forms.ValidationError("Enter Correct Password!")
        return old_password
        #check that the 2 password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't Match!")
        return password2

    def save(self, commit = True):
        # save the provided password in hashed format
        user = super(ChangeUserPasswordForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('email','full_name','phone_number','image')
        widgets = {
                'email':forms.TextInput(attrs={'class': 'form-control','readonly':'readonly'}),
                'phone_number': forms.TextInput(attrs={'class': 'js-max-length form-control payment_form', 'id':'phone_number'})
                }
    def save(self, commit = True):
        user = super(EditProfileForm, self).save(commit=False)
        if commit:
            user.save()
        return user

