from pickle import FALSE
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

from . import mpamba_service_bill, airtel_service_bill

class OpeningTime(models.Model):
    description = models.CharField(unique=True, max_length=120)
    open_time = models.TimeField()
    def __str__(self):
        return '{0}'.format(self.description)

class ClosingTime(models.Model):
    description = models.CharField(unique=True, max_length=120)
    closing_time = models.TimeField()
    def __str__(self):
        return '{0}'.format(self.description)


class Customer(models.Model):
    name = models.CharField(unique=True, max_length=120)
    phone_number = PhoneNumberField(null = True, blank = True)
    address = models.TextField(null=True)
    total_orders = models.IntegerField(default=0)

    def __str__(self):
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
    
    def check_if_ordered_item_is_in_refund_order(self):
        refund_order_item = RefundOrderItem.objects.get(order_id = self.order_id)  
        if refund_order_item != None:
            return True
        else:
            return False

@receiver(post_save, sender=OrderItem)
def update_orderitem_quantities(sender, instance, **kwargs):
    OrderItem.objects.filter(id=instance.id).update(ordered_item_price=instance.price, ordered_items_total = instance.amount)

class Payment(models.Model):
    payment_options =(
        ('Cash','Cash'),
        ('Mpamba', 'Mpamba'),
        ('Airtel Money', 'Airtel Money'),
        ('Bank', 'Bank'),
        
    )
    customer = models.ForeignKey(Customer, on_delete = models.SET_NULL, null = True)
    payment_mode = models.CharField(max_length = 15, choices = payment_options, default='Cash')
    order_id = models.CharField(max_length=20, null=True)
    order_type = models.CharField(max_length=20, null=True)
    service_fee = MoneyField(max_digits=14, decimal_places=2, default_currency='MWK', default= 0.0)
    paid_amount = MoneyField(max_digits=14, decimal_places=2, default_currency='MWK', default= 0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def get_service_fee(self):
        service_fee = Money(0.0, 'MWK')
        if self.payment_mode == 'Mpamba':
            service_fee = Money(mpamba_service_bill.get_service_fee(self.paid_amount), 'MWK')
            return  service_fee
        elif self.payment_mode == 'Airtel Money':
            service_fee = Money(airtel_service_bill.get_service_fee(self.paid_amount), 'MWK')
            return  service_fee
        else:
            return service_fee

    def __str__(self):
        return '{0}'.format(self.paid_amount)

order_type_options =(
        ('Cash','Cash'),
        ('Lay By', 'Lay By'),
    )
    
class Order(models.Model):
    def gen_code(self):
            return 'ORD%04d'%self.pk
    code = models.CharField(max_length=50, null=True, default="0000")
    order_type = models.CharField(max_length = 15, choices = order_type_options, default='Cash')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    items = models.ManyToManyField(OrderItem)
    ordered = models.BooleanField(default=False)
    payments = models.ManyToManyField(Payment)
    order_total_cost = MoneyField(max_digits=14, decimal_places=2, default_currency='MWK', default= 0.0)
    vat_p = models.FloatField(default=config.TAX_NAME)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_reference = models.CharField(max_length=50, null=True)

    @property
    def vat_cost(self):
        return self.get_vat_value

    def __str__(self):
        return '{1} {0}'.format(self.created_at, self.customer)

    @property
    def vat_rate(self):
        return float(config.TAX_NAME)
    
    @property
    def vat_rate_minus_100(self):
        return 100 - self.vat_p 
    
    @property
    def get_code(self):
        return self.gen_code
    
    def get_mpamba_bill(self):
        balance = self.get_balance()
        if balance > Money(0.0, 'MWK') and balance >= Money(50.0, 'MWK'):
            mpamba_bill = Money(0.0, 'MWK')
            mpamba_bill = mpamba_service_bill.get_mpamba_bill(balance)
            return mpamba_bill
        else:
            return self.get_balance()
    
    def get_airtel_bill(self):
        balance = self.get_balance()
        if balance > Money(0.0, 'MWK') and balance >= Money(50.0, 'MWK'):
            mpamba_bill = Money(0.0, 'MWK')
            mpamba_bill = airtel_service_bill.get_airtel_bill(balance)
            return mpamba_bill
        else:
            return self.get_balance()

    def get_airtel_money_service_fee(self):
        return "Airtel Money"

    def get_mpamba_service_fee(self):
        pass
    
    @property
    def get_vat_value(self):
        return self.vat_rate / 100.00 * self.order_total()

    @property
    def get_taxable_value(self):
        return self.vat_rate_minus_100 / 100.00 * self.order_total()
        
    def order_total_due(self):
        return self.get_taxable_value +  self.get_vat_value
    
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
        return self.order_type
    
    def total_paid_amount(self):
        sum_paid = Money(0.0, 'MWK')
        for payment in self.payments.all():
            if payment.payment_mode == "Mpamba":
                sum_paid += payment.paid_amount - payment.get_service_fee
            elif payment.payment_mode == "Airtel Money":
                sum_paid += payment.paid_amount - payment.get_service_fee
            else:
                sum_paid += payment.paid_amount
        return sum_paid

    def get_change(self):
        change = self.total_paid_amount() - self.order_total_due()
        return change
    
    def get_balance(self):
        balance = Money(0.0, 'MWK')
        sum_paid = self.total_paid_amount()
        if sum_paid < self.order_total_due():
            return self.order_total_due() - sum_paid
        else:
            return balance
    
    def default_amount_paid(self):
        default_money = Money(0.0, 'MWK')
        return default_money 

    @property
    def get_customer(self):
        return self.items.customer
    
    def check_if_refunded(self):
        refund_order = RefundOrder.objects.get(order_id = self.id)  
        if refund_order != None:
            return True
        else:
            return FALSE
    
    def amount_refunded(self):
        amount_refunded = Money(0.0, 'MWK')
        refund_order = RefundOrder.objects.get(order_id = self.id)
        if refund_order:
            return refund_order.total_refunded_amount
        else:
            return amount_refunded
    
    def get_balance_after_refund(self):
        return self.total_paid_amount() - self.amount_refunded()


class RefundPayment(models.Model):
    payment_options =(
        ('Cash','Cash'),
        ('Mpamba', 'Mpamba'),
        ('Airtel Money', 'Airtel Money'),
        ('Bank', 'Bank'),
    )
    payment_mode = models.CharField(max_length = 15, choices = payment_options, default='Cash')
    order_id = models.CharField(max_length=20, null=True)
    refund_amount = MoneyField(max_digits=14, decimal_places=2, default_currency='MWK', null = True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}'.format(self.refund_amount)

class RefundOrderItem(models.Model):
    order_id = models.CharField(default="", max_length=30)
    user = models.ForeignKey(CustomUser, on_delete = models.SET_NULL, null = True)
    item = models.ForeignKey(OrderItem, on_delete = models.CASCADE)
    return_quantity = models.IntegerField(default=0)
    initial_quantity = models.IntegerField(default=0)
    return_items_total_cost = MoneyField(max_digits=14, decimal_places=2, default_currency='MWK', default= 0.0)
    returned_time = models.DateTimeField(auto_now_add=True, null = True)
    restock_to_inventory = models.BooleanField(default=True)

    @property
    def price(self):
        return self.item.ordered_item_price

    @property
    def return_amount(self):
        amount = MoneyField()
        amount = self.return_quantity * self.price
        return amount

    def __str__(self):
        return f"{self.return_quantity} {self.item.item.unit} of {self.item.item.item_name}"
    
    @property
    def get_ordered_item_category(self):
        return self.item.item.category


class RefundOrder(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    code = models.CharField(max_length=50, null=True, default="0000")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    refunded_items = models.ManyToManyField(RefundOrderItem)
    refunded = models.BooleanField(default=False)
    ordered_total_cost = MoneyField(max_digits=14, decimal_places=2, default_currency='MWK', default= 0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payments = models.ManyToManyField(RefundPayment)
    reason_for_refund = models.CharField(max_length = 100, null= True,)

    def __str__(self):
        return '{1} {0}'.format(self.created_at, self.order_id.customer)

    @property
    def get_code(self):
        return self.order_id.get_code()
    
    @property
    def get_payment_mode(self):
        return self.order_type
    
    @property
    def total_refunded_amount(self):
        sum_paid = Money(0.0, 'MWK')
        for payment in self.payments.all():
            sum_paid += payment.refund_amount
        return sum_paid

    def default_amount_paid(self):
        default_money = Money(0.0, 'MWK')
        return default_money 

    def get_customer(self):
        return self.items.customer
    
  
    def refund_order_total(self):
        total = Money('0.0', 'MWK')
        for order_item in self.refunded_items.all():
            total += order_item.return_amount
        return total
    
    def balance_to_refund(self):
        total = Money('0.0', 'MWK')
        for order_item in self.refunded_items.all():
            total += order_item.return_amount
        return total - self.total_refunded_amount
    

# Update the last payment if it is more than the balance
@receiver(post_save, sender=Order)
def update_last_payment_on_order(sender, instance, **kwargs):
    if instance.ordered == True:
        last_payment = instance.payments.last()
        total_paid_amount = instance.total_paid_amount()
        if last_payment != None:
            previous_paid_amount =  total_paid_amount - last_payment.paid_amount
            balance_required = instance.order_total_due() -  previous_paid_amount
            Payment.objects.filter(id=last_payment.id).update(paid_amount = balance_required )

@receiver(post_save, sender=Order)
def save_layby_orders(sender, instance, **kwargs):
    if instance.payment_reference == "Lay By" and instance.paid_amount != instance.original_paid_amount:
        order = Order.objects.get(id=instance.id)
        
        layby_order, created = LayByOrders.objects.get_or_create(order_id = order)
        new_layby_order = LayByOrders.objects.get(id = layby_order.id)

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

class MoneyOutput(MoneyField):
    def from_db_value(self, value, expression, connection):
        return Money(value, 'MWK')
    
    




