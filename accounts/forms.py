from django import forms
from django.contrib.auth import get_user_model
from accounts.models import CustomUser
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.views.generic import UpdateView
from django.db import models
from django_countries.fields import CountryField
# from constance.admin import ConstanceAdmin, ConstanceForm, Config
from djmoney.forms.widgets import MoneyWidget
from django.contrib.auth import authenticate, login, logout, get_user_model
from pos.models import Customer
from phonenumber_field.formfields import PhoneNumberField



class UserAdminCreationForm(forms.ModelForm):
    # a form for creating new users. Includes all the required fields
    #plus a repeated password
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password Confirmation', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('email','full_name','image','phone_number','active', 'admin','staff','user_role')
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

class EditUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('email','full_name','phone_number','user_role','image','active', 'admin','staff')
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'js-max-length form-control payment_form', 'id':'phone_number'})
        }
    def save(self, commit = True):
        user = super(EditUserForm, self).save(commit=False)
        if commit:
            user.save()
        return user

class EditUserPermissionsForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('email','full_name','phone_number','user_role','image','active', 'admin','staff')
        widgets = {
                'email':forms.TextInput(attrs={'class': 'form-control','readonly':'readonly'}),
                'full_name':forms.TextInput(attrs={'class': 'form-control','readonly':'readonly'}),
                'phone_number':forms.TextInput(attrs={'class': 'form-control','readonly':'readonly'}),
                }

    def save(self, commit = True):
        user = super(EditUserPermissionsForm, self).save(commit=False)
        if commit:
            user.save()
        return user

# class LogInForm(forms.ModelForm):
#     class Meta:
#         model = CustomUser
#         fields = ('email','password',)
#         exclude = ('email',)
#         widgets = {
#                 'password':forms.PasswordInput(attrs={'class': 'form-control login-form',}),
#                 }

class UserLockForm(forms.Form):

    def __init__(self,request,*args,**kwargs):
        super (UserLockForm,self).__init__(*args,**kwargs)
        self.fields['username'] = forms.CharField(label='Username',max_length=100, initial= 'chiccochikaonda@gmail.com')

class UserAdminChangeForm(forms.ModelForm):
        #A form for updating users.Includes all the fields on the
        #user, but replaces the password field with admin's password hashe
        #displayfield
        password = ReadOnlyPasswordHashField()
        class meta:
            model = CustomUser
            fields = ('full_name','email','phone_number','image', 'password','active', 'admin', 'user_role')
            widgets = {
                'phone_number': forms.TextInput(attrs={'class': 'js-max-length form-control payment_form', 'id':'phone_number'})
        }
        def clean_password2(self):
                #regardless of what the user provides, return the initial Value
                #This is done here, rather than on the field, because the
                #field does not have access to the initial Value
            return self.initial("password")

