
from django.contrib import admin
from django.contrib.auth import get_user_model
from django import forms

from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from constance.admin import ConstanceAdmin, ConstanceForm, Config

from pos.models import Customer, OrderItem, Order, Payment,  LayByOrders, RefundOrder, RefundOrderItem, RefundPayment
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
    search_fields = ['item__item_name',]
    class Meta:
        model = OrderItem

admin.site.register(OrderItem, OrderItemAdmin)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('get_code','order_type','customer','get_code','user','vat_p','vat_cost','ordered','order_total_cost','get_balance','get_payment_mode','payment_reference','created_at','updated_at','vat_rate_minus_100')
    search_fields = ['order_date','customer']
    class Meta:
        model = CustomUser
admin.site.register(Order, OrderAdmin)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order_id','order_type','payment_mode','paid_amount','get_service_fee','customer','created_at', 'updated_at',)
    search_fields = ['payment_mode',]
    class Meta:
        model = Payment
admin.site.register(Payment, PaymentAdmin)

class LayByOrdersAdmin(admin.ModelAdmin):
    list_display = ('order_id','get_order_id', 'get_customer','get_order_price', 'get_sum_paid','get_order_balance', 'sum_paid','created_at','updated_at')
    search_fields = ['order_id',]
    class Meta:
        model =  LayByOrders
admin.site.register( LayByOrders,  LayByOrdersAdmin)



class RefundOrderAdmin(admin.ModelAdmin):
    list_display = ('order_id','code','user','refunded','ordered_total_cost','created_at','updated_at','total_refunded_amount','reason_for_refund')
    search_fields = ['item__item_name',]
    class Meta:
        model = RefundOrder

admin.site.register(RefundOrder, RefundOrderAdmin)

class RefundOrderItemAdmin(admin.ModelAdmin):
    list_display = ('order_id','user','item','initial_quantity','return_quantity','return_items_total_cost','returned_time','restock_to_inventory')
    search_fields = ['item__item_name',]
    class Meta:
        model = OrderItem

admin.site.register(RefundOrderItem, RefundOrderItemAdmin)

class RefundPaymentAdmin(admin.ModelAdmin):
    list_display = ('order_id','payment_mode','refund_amount','created_at', 'updated_at',)
    search_fields = ['payment_mode',]
    class Meta:
        model = RefundPayment
admin.site.register(RefundPayment, RefundPaymentAdmin)
