
from django.contrib import admin
from django.contrib.auth import get_user_model
from django import forms

from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.forms import UserAdminCreationForm
from constance.admin import ConstanceAdmin, ConstanceForm, Config

from pos.models import Customer, OrderItem, Order, Payment,  LayByOrders
from accounts.models import CustomUser
from .models import Quotation, QuotationItem

# Register your models here.
CustomUser = get_user_model()

class QuotationAdmin(admin.ModelAdmin):
    list_display = ('code','customer','user','order_date','expire_date','ordered','status', 'order_total_cost','vat_p','vat_cost')
    search_fields = ['name',]
    class Meta:
        model = Quotation
admin.site.register(Quotation, QuotationAdmin)

class QuotationItemAdmin(admin.ModelAdmin):
    list_display = ('user','item','user','ordered','quantity','ordered_item_price','ordered_items_total')
    search_fields = ['name',]
    class Meta:
        model = QuotationItem
admin.site.register(QuotationItem, QuotationItemAdmin)