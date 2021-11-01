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

from djmoney.money import Money
from accounts.models import CustomUser
from inventory.models import Item
from django.db.models.functions import Abs
from phonenumber_field.modelfields import PhoneNumberField

class Customer(models.Model):
    name = models.CharField(unique=True, max_length=120)
    phone_number = PhoneNumberField(null = True, blank = True, max_length = 16)
    # phone_number = models.CharField(max_length=15, null = True)
    total_orders = models.IntegerField(default=0)

    def __str__(self):
        # return '{0} ({1})'.format(self.name, self.phone_number)
        return '{0}'.format(self.name)
    
class OrderItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete = models.SET_NULL, null = True, related_name="user")
    item = models.ForeignKey(Item, on_delete = models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete = models.SET_NULL, null = True)
    ordered = models.BooleanField(default=False)
    quantity = models.IntegerField(default=0)
    ordered_item_price = MoneyField(max_digits=14, decimal_places=2, default_currency='MWK', default= 0.0)
    ordered_items_total = MoneyField(max_digits=14, decimal_places=2, default_currency='MWK', default= 0.0)
    order_id = models.ImageField(null = True)
    ordered_time = models.DateTimeField(auto_now_add=True, null = True)

    
    @property
    def price(self):
        return self.item.selling_price()

    @property
    def amount(self):
        amount = MoneyField()
        amount = self.quantity * self.item.selling_price()
        return amount

    @property
    def get_total_amount(self):
        return self.amount
    
    def get_item_discount(self):
        if self.item.discount_price:
            return self.quantity * self.item.price - self.quantity * self.item.discount_price
        else:
            return 0

    def __str__(self):
        return f"{self.quantity} {self.item.unit} of {self.item.item_name}"
    
    @property
    def get_ordered_item_category(self):
        return self.item.category



class Payment(models.Model):
    payment_options =(
        ('Cash','Cash'),
        ('Mpamba', 'Mpamba'),
        ('Airtel Money', 'Airtel Money'),
        
    )
    customer = models.ForeignKey(Customer, on_delete = models.SET_NULL, null = True)
    payment_mode = models.CharField(max_length = 15, choices = payment_options)
    paid_amount = MoneyField(max_digits=14, decimal_places=2, default_currency='MWK', null = True)
    reference = models.CharField(max_length = 30, null= True,)

    def __str__(self):
        return '{0}'.format(self.paid_amount)
    
    
class Order(models.Model):
    def gen_code(self):
            return 'ORD%04d'%self.pk
    
    code = models.CharField(max_length=50, null=True, default="0000")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null = True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null = True)
    # active = models.BooleanField(default=False)
    items = models.ManyToManyField(OrderItem)
    order_date = models.DateTimeField(auto_now_add=True)
    ordered = models.BooleanField(default=False)
    paid_amount = models.ForeignKey(Payment, on_delete=models.CASCADE, default = 1)
    order_total_cost = MoneyField(max_digits=14, decimal_places=2, default_currency='MWK', default= 0.0)
    vat_p = models.FloatField(default=config.TAX_NAME)
    vat_cost = MoneyField(max_digits=14, decimal_places=2, default_currency='MWK', default= 0.0)

    

    def __str__(self):
        return '{1} {0}'.format(self.order_date, self.customer)

    @property
    def vat_rate(self):
        return float(config.TAX_NAME)
    
    @property
    def get_code(self):
        return self.gen_code
    
    @property
    def reference(self):
        return self.paid_amount.reference

    @property
    def get_vat_value(self):
        return self.vat_rate / 100.00 * self.order_total()

        
    def order_total_due(self):
        return self.order_total() +  self.get_vat_value
    
    def service_fee(self):
        return float(config.SERVICE_FEE_A)
    
    def fee_value(self):
        return self.service_fee() / 100.00 * self.order_total()

    def order_airtel_money_total_due(self):
        return self.order_total() +  self.get_vat_value + self.fee_value()
    
    def order_mpamba_total_due(self):
        return self.order_total() +  self.get_vat_value + self.fee_value()

    def order_total(self):
        total = Money('0.0', 'MWK')
        for order_item in self.items.all():
            total += order_item.amount
        return total 
    
    def all_items_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.amount
        return total

    def get_total_discount(self):
        discount_total = 0
        for ordered_item in self.items.all():
            discount_total += ordered_item.get_item_discount()
        return discount_total
    
    @property
    def get_payment_mode(self):
        return self.paid_amount.payment_mode
    
    def get_change(self):
        change = self.paid_amount.paid_amount - self.order_total_due()
        return change
    
    def get_balance(self):
        default_amount = Money(0.0, 'MWK')
        if self.paid_amount.paid_amount < self.order_total_due():
            return -1 * (self.paid_amount.paid_amount - self.order_total_due())
        else:
            return default_amount
    
    
    def default_amount_paid(self):
        default_money = Money(0.0, 'MWK')
        # default_money = ("MWK", 0.0)
        return default_money 

    # @property()
    def get_customer(self):
        return self.items.customer
