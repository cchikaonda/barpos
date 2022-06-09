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
    cost_price = MoneyField(max_digits=14, decimal_places=2, default_currency='MWK', default=0)
    total_cost_price = MoneyField(max_digits=14, decimal_places=2, default_currency='MWK', default=0)
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

    def get_total_cost_of_items(self):
        return self.get_cost_price * self.quantity_at_hand
            
    def get_expected_revenue(self):
        return self.selling_price() * self.quantity_at_hand
    
    @property
    def get_cost_price(self):
        stock = Stock.objects.filter(item = self.id)
        print(stock)
        if stock:
            return stock.last().ordered_price
        else:
            return self.price * 0.7
    
    @property
    def get_total_cost_price(self):
        return self.get_cost_price * self.quantity_at_hand
    


    
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

    def get_add_to_cart_quotation_url(self):
        return reverse('add_to_cart_quotation', kwargs={'slug': self.slug})

    def get_remove_from_cart_quotation_url(self):
        return reverse('remove_from_cart_quotation', kwargs={'slug': self.slug})


class BatchNumber(models.Model):
    batch_number = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return '{0}'.format(self.batch_number)



class Stock(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    batch = models.ForeignKey(BatchNumber, on_delete=models.SET_NULL, null=True, default=1)
    supplier_name = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    ordered_price = MoneyField(max_digits=14, decimal_places=2, default_currency='MWK', default= 1)
    previous_quantity = models.IntegerField(default=0)
    stock_in = models.IntegerField(default=0)
    new_quantity = models.IntegerField(default=0)
    unit_quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_cost_of_items = MoneyField(max_digits=14, decimal_places=2, default_currency='MWK', default=0)

    class Meta:
        ordering = ['-created_at']

    def __init__(self, *args, **kwargs):
        super(Stock, self).__init__(*args, **kwargs)
        self.original_updated_at = self.updated_at
    

    def __str__(self):
        return self.item.item_name

    def get_total_stock(self):
        return self.stock_in * self.unit_quantity
    
    def get_item_quantity_at_hand(self):
        return self.item.quantity_at_hand
    
    def get_item_ordered_price(self):
        return self.ordered_price
    

    @property
    def get_total_cost_of_items(self):
        return self.stock_in * self.ordered_price

    @staticmethod
    def get_all_stocks():
        return Stock.objects.all()
        
    @staticmethod
    def get_all_stocks_with_batch_id(batch_id):
        if batch_id:
            return Stock.objects.filter(batch=batch_id)
        else:
            return Stock.get_all_stocks()
        

    

@receiver(post_save, sender=Stock)
def update_quantity_at_hand_in_inventory(sender, instance, **kwargs):
    instance.previous_quantity = get_item_quantity_at_hand(instance)
    instance.item.cost_price = instance.item.get_cost_price
    instance.item.total_cost_price = instance.item.get_total_cost_price
    instance.item.save()



@receiver(post_save, sender=Stock)
def update_quantities_in_stock(sender, instance, **kwargs):
    if instance.previous_quantity == 0:
        old_stock = Stock.objects.get(id=instance.id)
        new_quantity = old_stock.previous_quantity + old_stock.get_total_stock()
        Stock.objects.filter(id=instance.id).update(new_quantity=new_quantity, total_cost_of_items = instance.get_total_cost_of_items)
        instance.item.quantity_at_hand = new_quantity
        instance.item.ordered_price = instance.ordered_price
        instance.item.save() 
    else:
        instance.previous_quantity = get_item_quantity_at_hand(instance)
        previous_quantity = get_item_quantity_at_hand(instance)
        new_quantity = previous_quantity + instance.get_total_stock()
        Stock.objects.filter(id=instance.id).update(new_quantity=new_quantity, previous_quantity = previous_quantity, total_cost_of_items = instance.get_total_cost_of_items)
        instance.item.ordered_price = instance.ordered_price
        instance.item.quantity_at_hand = new_quantity
        instance.item.save()


def get_item_quantity_at_hand(instance):
    return instance.item.quantity_at_hand


