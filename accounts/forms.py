from django import forms
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
from django.contrib.auth.models import Group
from django.contrib.admin.widgets import FilteredSelectMultiple

from django import VERSION, forms
from django.utils.translation import gettext_lazy as _

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import  Permission,User

CustomUser = get_user_model()


User = get_user_model()


# Create ModelForm based on the Group model.
class GroupAdminForm(forms.ModelForm):
    class Meta:
        model = Group
        exclude = []

    # Add the users field.
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        # Use the pretty 'filter_horizontal widget'.
        widget=FilteredSelectMultiple('users', False),
        label=_('Users'),
    )

    def __init__(self, *args, **kwargs):
        # Do the normal form initialisation.
        super(GroupAdminForm, self).__init__(*args, **kwargs)
        # If it is an existing group (saved objects have a pk).
        if self.instance.pk:
            # Populate the users field with the current Group users.
            self.fields['users'].initial = self.instance.user_set.all()

    def save_m2m(self):
        # Add the users to the Group.
        # Deprecated in Django 1.10: Direct assignment to a reverse foreign key
        #                            or many-to-many relation
        if VERSION < (1, 9):
            self.instance.user_set = self.cleaned_data['users']
        else:
            self.instance.user_set.set(self.cleaned_data['users'])

    def save(self, *args, **kwargs):
        # Default save
        instance = super(GroupAdminForm, self).save()
        # Save many-to-many data
        self.save_m2m()
        return instance

class UserAdminCreationForm(forms.ModelForm):
    # a form for creating new users. Includes all the required fields
    #plus a repeated password
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password Confirmation', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('email','full_name','image','phone_number','active', 'admin','staff','superuser','user_role','groups')
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
        fields = ('email','full_name','phone_number','user_role','image','active', 'admin','staff','superuser','groups')
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

class UserAdminChangeForm(forms.ModelForm):
        #A form for updating users.Includes all the fields on the
        #user, but replaces the password field with admin's password hashe
        #displayfield
        password = ReadOnlyPasswordHashField()
        class meta:
            model = CustomUser
            fields = ('full_name','email','phone_number','image', 'password','active', 'admin', 'user_role','groups')
            widgets = {
                'phone_number': forms.TextInput(attrs={'class': 'js-max-length form-control payment_form', 'id':'phone_number'})
        }
        def clean_password2(self):
                #regardless of what the user provides, return the initial Value
                #This is done here, rather than on the field, because the
                #field does not have access to the initial Value
            return self.initial("password")


class EditUserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)

        def get_label(obj):
            permission_name = str(obj).split('|')[2].strip()
            model_name = permission_name.split(' ')[2].strip()
            return '%s | %s' % (model_name.title(), permission_name)

        User = get_user_model()
        content_type = ContentType.objects.get_for_model(CustomUser)
        self.fields['user_permissions'].queryset = Permission.objects.filter(content_type=content_type)
        self.fields['user_permissions'].widget.attrs.update({'class': 'permission-select'})
        self.fields['user_permissions'].help_text = None
        self.fields['user_permissions'].label = "Label"
        self.fields['user_permissions'].label_from_instance = get_label

    def save(self, commit=True):
        user_instance = super(EditUserForm, self).save(commit)
        user_instance.save()
        user_instance.user_permissions.set(self.cleaned_data.get('user_permissions'))
        return user_instance

    class Meta:
        model = get_user_model()
        fields = ['email', 'phone_number','user_permissions']

        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'style': 'width: 300px;'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 300px;'}),
            'user_permissions': forms.SelectMultiple(attrs={'style': 'width: 350px; height: 200px;'})
        }