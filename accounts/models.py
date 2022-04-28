from django.db import models
from django.conf import settings
from djmoney.models.fields import MoneyField
from django.contrib.auth.models import User
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.shortcuts import reverse
from constance import config
from datetime import date
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import Group

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, full_name = None ,user_role = None,phone_number = None,password = None, is_active = True, is_staff = True, is_admin = False, is_superuser = False):
        if not email:
            raise ValueError ("Users must have an email address")
        if not password:
            raise ValueError ("Users must have a password")
        if not full_name:
            raise ValueError (" Users must have a password")

        user_obj = self.model(
            email = self.normalize_email(email),
            full_name = full_name,
            phone_number = phone_number,
            user_role = user_role,
        )
        user_obj.set_password(password) # change user password
        user_obj.admin = is_admin
        user_obj.active = is_active
        user_obj.superuser = is_superuser
        user_obj.staff = is_staff
        user_obj.save(using=self._db)
        return user_obj

    def create_superuser(self, email,full_name = None,phone_number =None, password = None, user_role = None):
        user = self.create_user(
                email,
                full_name,
                phone_number,
                password = password,
                is_admin=True,
                is_active = True,
                is_superuser = True,
                is_staff = True,
        )
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255, blank = True, null=True)
    roles =(
        ('Admin','Admin'),
        ('User', 'General User'),
    )
    user_role = models.CharField(max_length = 15, choices = roles, default = "General User")
    phone_number = PhoneNumberField(null = True, blank = True)
    username = None
    active = models.BooleanField(default=True) #can login
    admin = models.BooleanField(default=False) # Adminstrator
    superuser = models.BooleanField(default=False) #superuser
    staff = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(default = "avatar0.jpg", null = True, blank = True)
    group = Group.add_to_class('description', models.CharField(max_length=180,null=True, blank=True))
    USERNAME_FIELD = 'email' #loginuser
    REQUIRED_FIELDS = ['full_name','phone_number',]


    objects = UserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_superuser(self):
        return self.superuser

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active
    
    @property
    def is_staff(self):
        return self.staff
    
    
    
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url





    

