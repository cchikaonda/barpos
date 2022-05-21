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
from accounts.models import CustomUser
from pos.models import OrderItem, Customer
from inventory.models import Item, ItemCategory




class QuotationItem(models.Model):
    quotation_id = models.CharField(default="", max_length=30)
    user = models.ForeignKey(CustomUser, on_delete = models.SET_NULL, null = True)
    item = models.ForeignKey(Item, related_name = 'order_item', on_delete = models.PROTECT)
    ordered = models.BooleanField(default=False)
    quantity = models.IntegerField(default=1)
    ordered_item_price = MoneyField(max_digits=14, decimal_places=2, default_currency='MWK', default= 0.0)
    ordered_items_total = MoneyField(max_digits=14, decimal_places=2, default_currency='MWK', default= 0.0)
    
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

class Quotation(models.Model):
    def gen_code(self):
            return 'QTD%04d'%self.pk
    code = models.CharField(max_length=50, null=True, default="0000")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    items = models.ManyToManyField(QuotationItem)
    order_date = models.DateTimeField(auto_now_add=True)
    expire_date = models.DateField(null=True)
    ordered = models.BooleanField(default=False)
    choices =(
        ('Pending','Pending ...'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled')
    )
    status = models.CharField(max_length = 15, choices = choices, default = "Pending ...")
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
    def is_order_expire(self):
        if self.expire_date:
            if self.expire_date < date.today():
                return True
            else:
                return False 
        else:
            return False
        

    def get_vat_value(self):
        return self.vat_rate / 100.00 * self.order_total()
        


    def order_total_due(self):
        return self.order_total() +  self.get_vat_value()

    def order_total(self):
        total = 0
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
    def vat_rate_minus_100(self):
        return 100 - self.vat_p 
    @property
    def get_vat_value(self):
        return self.vat_rate / 100.00 * self.order_total()

    @property
    def get_taxable_value(self):
        return self.vat_rate_minus_100 / 100.00 * self.order_total()
        
    def order_total_due(self):
        return self.get_taxable_value +  self.get_vat_value
    