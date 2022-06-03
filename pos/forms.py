from dataclasses import field
from django import forms
from django.contrib.auth import get_user_model
from accounts.models import CustomUser
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.views.generic import UpdateView
from django.db import models
from django_countries.fields import CountryField
# from constance.admin import ConstanceAdmin, ConstanceForm, Config
from djmoney.forms.widgets import MoneyWidget
from django.contrib.auth import authenticate, login, logout, get_user_model
from pos.models import Customer, LayByOrders, Payment, Order, RefundOrder, RefundOrderItem, RefundPayment
from inventory.models import Item

class CustomMoneyWidget(MoneyWidget):
    def format_output(self, rendered_widgets):
        return ('<div class="row form-group">'
                    '<div class="col-sm-12 ">%s</div>'
                    '<div class="col-sm-12 ">%s</div>'
                '</div>') % tuple(rendered_widgets)


# class AddPaymentForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         super(AddPaymentForm, self).__init__(*args, **kwargs)
#         paid_amount, currency = self.fields['paid_amount'].fields
#         self.fields['paid_amount'].widget = CustomMoneyWidget(amount_widget = paid_amount.widget, currency_widget = currency.widget)
#     class Meta:
#         model = Payment
#         fields = ('payment_mode','paid_amount','customer')
#         widgets = {
#                 'paid_amount': forms.TextInput(attrs={'class': 'form-control pos_form',}),
#                 'payment_mode': forms.Select(attrs={'class': 'form-control pos_form',}),
#                 'paid_amount': forms.TextInput(attrs={'class': 'form-control pos_form', 'readonly':'readonly'}),
#         }
    
class AddPaymentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddPaymentForm, self).__init__(*args, **kwargs)
        paid_amount, currency = self.fields['paid_amount'].fields
        self.fields['paid_amount'].widget = CustomMoneyWidget(amount_widget = paid_amount.widget, currency_widget = currency.widget)
    class Meta:
        model = Payment
        fields = ('payment_mode','paid_amount','customer')
        widgets = {
                'paid_amount': forms.TextInput(attrs={'class': 'form-control pos_form',}),
                'payment_mode': forms.Select(attrs={'class': 'form-control pos_form',}),
                'paid_amount': forms.TextInput(attrs={'class': 'form-control pos_form',}),
        }

class CashPaymentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddPaymentForm, self).__init__(*args, **kwargs)
        paid_amount, currency = self.fields['paid_amount'].fields
        self.fields['paid_amount'].widget = CustomMoneyWidget(amount_widget = paid_amount.widget, currency_widget = currency.widget)
    class Meta:
        model = Payment
        fields = ('payment_mode','paid_amount',)
        widgets = {
                'paid_amount': forms.TextInput(attrs={'class': 'form-control pos_form',}),
                'payment_mode': forms.Select(attrs={'class': 'form-control pos_form',}),
        }

class OrderTypeForm(forms.ModelForm):
     class Meta:
         model = Order
         fields = ('order_type',)
         widgets = {
                  'order_type': forms.Select(attrs={'class': 'form-control pos_form'})
          }


class SearchForm(forms.ModelForm):
     class Meta:
         model = Item
         fields = ('barcode',)
         widgets = {
                  'barcode': forms.TextInput(attrs={'class': 'form-control pos_form','placeholder':'Search Item by Name or Barcode','id':'search-form',
                  })
          }

class AddCustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('name', 'phone_number','address')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'pos_form'}),
            'phone_number': forms.TextInput(attrs={'class': 'pos_form', 'id':'phone_number'})
        }

class AddLayByPaymentForm(forms.ModelForm):
     def __init__(self, *args, **kwargs):
        super(AddLayByPaymentForm, self).__init__(*args, **kwargs)
        paid_amount, currency = self.fields['paid_amount'].fields
        self.fields['paid_amount'].widget = CustomMoneyWidget(amount_widget = paid_amount.widget, currency_widget = currency.widget)
     class Meta:
        model = Payment
        fields = ('payment_mode','paid_amount','customer')
        widgets = {
                'paid_amount': forms.TextInput(attrs={'class': 'form-control pos_form',}),
                'payment_mode': forms.TextInput(attrs={'class': 'form-control pos_form','readonly':'readonly'}),
        
        }

class RefundOrderItemForm(forms.ModelForm):
    class Meta:
        model = RefundOrderItem
        fields = ['order_id', 'user', 'item','return_quantity','initial_quantity','return_items_total_cost',]
        name = forms.CharField()
        date = forms.DateInput()
        members = forms.ModelMultipleChoiceField(
        queryset=RefundOrderItem.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )


class AddRefundPaymentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddRefundPaymentForm, self).__init__(*args, **kwargs)
        refund_amount, currency = self.fields['refund_amount'].fields
        self.fields['refund_amount'].widget = CustomMoneyWidget(amount_widget = refund_amount.widget, currency_widget = currency.widget)
    class Meta:
        model = RefundPayment
        fields = ('payment_mode','refund_amount')
        widgets = {
                'payment_mode': forms.Select(attrs={'class': 'form-control pos_form',}),
                'refund_amount': forms.TextInput(attrs={'class': 'form-control pos_form',}),
        }

class ReasonForRefund(forms.ModelForm):
    class Meta:
        model = RefundOrder
        fields = {'reason_for_refund',}
        widgets = {
                'reason_for_refund': forms.TextInput(attrs={'class': 'form-control pos_form',}),
        }

class RestockItemForm(forms.ModelForm):
    class Meta:
        model = RefundOrderItem
        fields = {'restock_to_inventory',}
        widgets = {
            'restock_to_inventory': forms.CheckboxInput,
        }


         