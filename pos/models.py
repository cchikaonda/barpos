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
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


class Customer(models.Model):
    name = models.CharField(unique=True, max_length=120)
    phone_number = PhoneNumberField(null = True, blank = True)
    address = models.TextField(null=True)
    total_orders = models.IntegerField(default=0)

    def __str__(self):
        # return '{0} ({1})'.format(self.name, self.phone_number)
        return '{0}'.format(self.name)
    
class OrderItem(models.Model):
    order_id = models.CharField(default="", max_length=30)
    user = models.ForeignKey(CustomUser, on_delete = models.SET_NULL, null = True)
    item = models.ForeignKey(Item, on_delete = models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete = models.SET_NULL, null = True)
    ordered = models.BooleanField(default=False)
    quantity = models.IntegerField(default=0)
    ordered_item_price = MoneyField(max_digits=14, decimal_places=2, default_currency='MWK', default= 0.0)
    ordered_items_total = MoneyField(max_digits=14, decimal_places=2, default_currency='MWK', default= 0.0)
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

@receiver(post_save, sender=OrderItem)
def update_orderitem_quantities(sender, instance, **kwargs):
    OrderItem.objects.filter(id=instance.id).update(ordered_item_price=instance.price, ordered_items_total = instance.amount)



class Payment(models.Model):
    payment_options =(
        ('Cash','Cash'),
        ('Mpamba', 'Mpamba'),
        ('Airtel Money', 'Airtel Money'),
        ('Lay By', 'Lay By'),
        
    )
    customer = models.ForeignKey(Customer, on_delete = models.SET_NULL, null = True)
    payment_mode = models.CharField(max_length = 15, choices = payment_options)
    paid_amount = MoneyField(max_digits=14, decimal_places=2, default_currency='MWK', null = True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reference = models.CharField(max_length = 30, null= True,)



    def __str__(self):
        return '{0}'.format(self.paid_amount)


    
    
class Order(models.Model):
    def gen_code(self):
            return 'ORD%04d'%self.pk
    code = models.CharField(max_length=50, null=True, default="0000")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    order_date = models.DateTimeField(auto_now_add=True)
    ordered = models.BooleanField(default=False)
    paid_amount = models.ForeignKey(Payment, on_delete=models.CASCADE, default = 1)
    order_total_cost = MoneyField(max_digits=14, decimal_places=2, default_currency='MWK', default= 0.0)
    vat_p = models.FloatField(default=config.TAX_NAME)
    vat_cost = MoneyField(max_digits=14, decimal_places=2, default_currency='MWK', default= 0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_reference = models.CharField(max_length=50, null=True)

    def __init__(self, *args, **kwargs):
        super(Order, self).__init__(*args, **kwargs)
        self.original_paid_amount = self.paid_amount

    

    def __str__(self):
        return '{1} {0}'.format(self.order_date, self.customer)

    @property
    def vat_rate(self):
        return float(config.TAX_NAME)
    
    @property
    def vat_rate_minus_100(self):
        return 100 - self.vat_p 
    
    
    @property
    def get_code(self):
        return self.gen_code
    
   
    @property
    def get_vat_value(self):
        return self.vat_rate / 100.00 * self.order_total()

    @property
    def get_taxable_value(self):
        return self.vat_rate_minus_100 / 100.00 * self.order_total()
        
    def order_total_due(self):
        return self.get_taxable_value +  self.get_vat_value
    
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

# @receiver(post_save, sender=Payment)
# def update_ordered_date_if_payment_is_done(sender, instance, **kwargs):
#     instance.paid_amount


@receiver(post_save, sender=Order)
def save_layby_orders(sender, instance, **kwargs):
    if instance.payment_reference == "Lay By" and instance.paid_amount != instance.original_paid_amount:
        order = Order.objects.get(id=instance.id)
        
        layby_order, created = LayByOrders.objects.get_or_create(order_id = order)
        new_layby_order = LayByOrders.objects.get(id = layby_order.id)

        # sum_paid_and_balance = order.paid_amount.paid_amount + new_layby_order.get_order_balance
        
        
        if order.paid_amount.paid_amount > new_layby_order.get_order_balance and order.ordered == True:
            paid = Payment()
            paid.paid_amount = new_layby_order.get_order_balance
            paid.save()
        else:
            paid = Payment()
            paid.paid_amount = order.paid_amount.paid_amount
            paid.save()

        new_layby_order.payments.add(paid)

        total = 0
        for payment in new_layby_order.payments.all():
            total += payment.paid_amount
        LayByOrders.objects.filter(id = layby_order.id).update(sum_paid = total)
        
        order_payment2 = Payment()
        order_payment2.paid_amount = total
        order_payment2.save()
        Order.objects.filter(id=instance.id).update(paid_amount=order_payment2)


        # znew_layby_order.update(sum_paid = total)
        # layby_order.update(get_sum_paid = payment)

    # OrderItem.objects.filter(id=instance.id).update(ordered_item_price=instance.price, ordered_items_total = instance.amount)

class LayByOrders(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    payments = models.ManyToManyField(Payment)
    sum_paid = MoneyField(max_digits=14, decimal_places=2, default_currency='MWK', default= 0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{1} {0}'.format(self.order_id.id, self.order_id.code)
    

    @property
    def get_order_id(self):
        return self.order_id.get_code
    
    @property
    def get_customer(self):
        return self.order_id.customer
    
    @property
    def get_order_price(self):
        return self.order_id.order_total_cost

    @property
    def get_sum_paid(self):
        total = 0
        for payment in self.payments.all():
            total += payment.paid_amount
        return total
    
    @property
    def get_order_balance(self):
        return self.get_order_price - self.get_sum_paid
    
    




