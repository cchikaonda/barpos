from django.contrib import admin
from django.contrib.auth import get_user_model
from django import forms

from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserAdminCreationForm, UserAdminChangeForm
from constance.admin import ConstanceAdmin, ConstanceForm, Config

from accounts.models import CustomUser

# Register your models here.
CustomUser = get_user_model()

class CustomeUserAdmin(BaseUserAdmin):
    #the forms to add and change user instances
    change_form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    #the fields to be used in dispaying the user models
    #these override the definitions on the base UserAdmin
    #that reference specific fields on auth.user
    list_display = ('full_name','email', 'admin','superuser','active','staff','phone_number', 'image','password')
    list_filter = ('superuser','admin','active','staff','staff')
    fieldsets = (
        (None, {'fields': ('email',)}),
        ('Personal information', {'fields': ('full_name','phone_number','image')}),
        ('Permissions', {'fields': ('superuser','admin', 'active','staff','password')}),
    )
    #add_fieldsets is not a standard ModelAdmin attribute. UserAdmins
    #overrides get_fieldsets to use this attribute when creating a user
    add_fieldsets = (
        (None,{
             'classes': ('wide',),
             'fields': ('email','full_name','phone_number','image','admin','active','superuser','staff','password1', 'password2'),}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

admin.site.register(CustomUser, CustomeUserAdmin)
admin.site.unregister(Group)






