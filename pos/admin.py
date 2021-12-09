
from django.contrib import admin
from django.contrib.auth import get_user_model
from django import forms

from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.forms import UserAdminCreationForm, UserAdminChangeForm
from constance.admin import ConstanceAdmin, ConstanceForm, Config

from pos.models import Customer, OrderItem, Order, Payment
from accounts.models import CustomUser

# Register your models here.
CustomUser = get_user_model()

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id','name','total_orders','phone_number','address')
    search_fields = ['name',]
    class Meta:
        model = Customer
admin.site.register(Customer, CustomerAdmin)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order_id','user','customer','item','get_ordered_item_category','quantity','ordered_item_price','ordered_items_total','ordered','ordered_time')
    search_fields = ['user',]
    class Meta:
        model = OrderItem

admin.site.register(OrderItem, OrderItemAdmin)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer','get_code','user','vat_p','vat_cost','order_date','ordered','order_total_cost','sum_paid_amount','sum_lay_by_payments','get_balance','created_at','vat_rate_minus_100','payment_mode')
    search_fields = ['order_date','customer']
    class Meta:
        model = CustomUser
admin.site.register(Order, OrderAdmin)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_mode','paid_amount', 'reference','customer','created_at', 'updated_at',)
    search_fields = ['payment_mode',]
    class Meta:
        model = Payment
admin.site.register(Payment, PaymentAdmin)




