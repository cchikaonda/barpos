from django.contrib import admin
from django.contrib.auth import get_user_model
from django import forms

from django.contrib.auth.models import Group

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import *
from inventory.forms import *
from constance.admin import ConstanceAdmin, ConstanceForm, Config

from accounts.models import CustomUser
from constance.admin import ConstanceAdmin, ConstanceForm, Config
from .forms import GroupAdminForm

class CustomConfigForm(ConstanceForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

#... do stuff to make your settings form nice ...
# class ConfigAdmin(ConstanceAdmin):
#     change_list_form = CustomConfigForm
#     change_list_template = 'admin/config/settings.html'
# admin.site.unregister([Config])
# admin.site.register([Config], ConfigAdmin)

# Register your models here.
User = get_user_model()

class CustomUserAdmin(BaseUserAdmin):
    #the forms to add and change user instances
    add_form = UserAdminCreationForm
    #the fields to be used in dispaying the user models
    #these override the definitions on the base UserAdmin
    #that reference specific fields on auth.user
    list_display = ('full_name','email', 'admin','superuser','active','staff','phone_number', 'image','password',)
    list_filter = ('superuser','admin','active','staff','staff','groups')
    fieldsets = (
        (None, {'fields': ('email',)}),
        ('Personal information', {'fields': ('full_name','phone_number','image')}),
        ('Permissions', {'fields': ('superuser','admin', 'active','staff','password','groups')}),
    )
    #add_fieldsets is not a standard ModelAdmin attribute. UserAdmins
    #overrides get_fieldsets to use this attribute when creating a user
    add_fieldsets = (
        (None,{
             'classes': ('wide',),
             'fields': ('email','full_name','phone_number','image','admin','active','superuser','staff','groups','password1', 'password2'),}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

admin.site.register(CustomUser, CustomUserAdmin)

# Unregister the original Group admin.
admin.site.unregister(Group)

# Create a new Group admin.
class GroupAdmin(admin.ModelAdmin):
    # Use our custom form.
    form = GroupAdminForm
    # Filter permissions horizontal as well.
    filter_horizontal = ['permissions']

# Register the new Group ModelAdmin.
admin.site.register(Group, GroupAdmin)






