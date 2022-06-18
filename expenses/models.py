from django.db import models
from django.conf import settings
from djmoney.models.fields import MoneyField
from django.contrib.auth.models import User
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager
)
from django.shortcuts import reverse
from constance import config
from datetime import date

from pymysql import NULL

from accounts.models import CustomUser
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from inventory.models import BatchNumber


class ExpenseCategory(models.Model):
    category_name = models.CharField(max_length=50)
    category_description = models.CharField(max_length=100)
    
    def __str__(self):
        return self.category_name
    
    @staticmethod
    def get_all_expense_categories():
        return ExpenseCategory.objects.all()

class Expense(models.Model):
    payment_options =(
        ('Cash','Cash'),
        ('Mpamba', 'Mpamba'),
        ('Airtel Money', 'Airtel Money'),
        ('Bank', 'Bank'),
        
    )
    batch_number = models.ForeignKey(BatchNumber, on_delete=models.CASCADE)
    payment_mode = models.CharField(max_length = 15, choices = payment_options, default='Cash')
    expense_name = models.CharField(max_length=100)
    expense_description = models.CharField(max_length=100)
    amount = MoneyField(max_digits=14, decimal_places=2, default_currency='MWK', null = True)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    paid_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField()
    

    def __str__(self):
        return self.expense_name
    
    @staticmethod
    def get_all_expense():
        return Expense.objects.all().order_by('expense_name')

    @staticmethod
    def get_all_items_by_category_id(category_id):
        if category_id:
            return Expense.objects.filter(category=category_id).order_by('expense_name')
        else:
            return Expense.get_all_expense()
    

    
