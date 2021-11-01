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
from phonenumber_field.modelfields import PhoneNumberField

class Supplier(models.Model):
    name = models.CharField(unique=True, max_length=120)
    address = models.CharField(max_length=120)
    phone_number = PhoneNumberField(null = True, blank = True)
    description = models.CharField(max_length=70)

    def __str__(self):
        return '{0}'.format(self.name)

class Unit(models.Model):
    unit_short_name = models.CharField(max_length=10)
    unit_description = models.CharField(max_length=100)
    def __str__(self):
        return self.unit_short_name

class ItemCategory(models.Model):
    category_name = models.CharField(max_length=50)
    category_description = models.CharField(max_length=100)
    btn_colour = (
        ('Black', 'dark'),
        ('Orange', 'warning'),
        ('Red', 'danger'),
        ('Blue', 'primary'),
        ('Light Black', 'light'),
        ('Light Blue', 'info'),
        ('Green', 'success')
    )
    category_colour = models.CharField(max_length=15, choices=btn_colour, default="Blue")
    @property
    def button_colour(self):
        return [i[0] for i in ItemCategory._meta.get_field('category_colour').choices if i[0] == self.category_colour][
            0]

    @property
    def category_link_colour(self):
        return [i[1] for i in ItemCategory._meta.get_field('category_colour').choices if i[0] == self.category_colour][
            0]

    def __str__(self):
        return self.category_name
    
    @staticmethod
    def get_all_item_categories():
        return ItemCategory.objects.all()


class Item(models.Model):
    item_name = models.CharField(max_length=100)
    item_description = models.CharField(max_length=100)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    barcode = models.IntegerField(null=False, unique=True)
    image = models.ImageField(default="ecom_product6_b.png", upload_to='items/', null=True, blank=True)
    # supplier_name = models.ForeignKey(Supplier, on_delete=models.CASCADE, blank=True)
    # ordered_price = MoneyField(max_digits=14, decimal_places=2, default_currency='MWK')
    price = MoneyField(max_digits=14, decimal_places=2, default_currency='MWK')
    discount_price = MoneyField(max_digits=14, null=True, blank=True, decimal_places=2, default_currency='MWK')
    category = models.ForeignKey(ItemCategory, on_delete=models.CASCADE)
    quantity_at_hand = models.IntegerField(default=0)
    reorder_level = models.IntegerField()
    active = models.BooleanField(default=True)
    slug = models.SlugField()

    def __str__(self):
        return self.item_name

    def selling_price(self):
        if self.discount_price:
            return self.discount_price
        else:
            return self.price

    
    @staticmethod
    def get_all_items():
        return Item.objects.all().order_by('item_name')

    @staticmethod
    def get_all_items_by_category_id(category_id):
        if category_id:
            return Item.objects.filter(category=category_id).order_by('item_name')
        else:
            return Item.get_all_items()
        
    def get_add_to_cart_url(self):
        return reverse('add_to_cart', kwargs={'slug': self.slug})

    def get_remove_from_cart_url(self):
        return reverse('remove_from_cart', kwargs={'slug': self.slug})


class Stock(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    batch = models.IntegerField(null=False)
    supplier_name = models.ForeignKey(Supplier, on_delete=models.CASCADE, blank=True)
    ordered_price = MoneyField(max_digits=14, decimal_places=2, default_currency='MWK')