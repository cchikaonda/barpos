from django.shortcuts import render,redirect, get_object_or_404
from inventory.models import ItemCategory, Unit, Item, Supplier
from pos.models import Customer, LayByOrders, OrderItem, Order, Payment, RefundOrder, RefundOrderItem, RefundPayment
from django.contrib import messages
from constance import config
from django.utils import timezone
from datetime import date, timedelta, datetime
from django.core.exceptions import ObjectDoesNotExist
from pos.forms import AddPaymentForm, CashPaymentForm, SearchForm, AddCustomerForm, AddLayByPaymentForm, AddRefundPaymentForm
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.core import serializers
import json
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from accounts.admin import CustomConfigForm
from barpos import settings
import time
from djmoney.money import Money
from django.template.loader import render_to_string
from django.http import HttpResponse


@login_required
def refunds_list(request):
    refunds_orders = RefundOrder.objects.all()
    context = {
        'refunds_orders':refunds_orders,
    }
    return render(request, 'refunds_list.html', context=context)


@login_required
def refund_order(request, id):
    paid_order = get_object_or_404(Order,id=id)
    request.session['refund_order'] = paid_order.id
    code = paid_order.get_code()
    refund_order = RefundOrder.objects.filter(code = code)
    refund_payment_form = AddRefundPaymentForm()
    

    if refund_order.exists():
        order = refund_order[0]
        refund_order_items = get_items_in_refund_order(order)
        refund_order2 = RefundOrder.objects.get(code = code)
        context = {
            'refund_order':refund_order,
            'paid_order':paid_order,
            'refund_order_items':refund_order_items,
            'refund_order2':refund_order2,
            'refund_payment_form':refund_payment_form,
        }
        return render(request, 'refunds/refund_order.html', context=context)
    else:
        context = {
        'refund_order':refund_order,
        'paid_order':paid_order,
        'refund_payment_form':refund_payment_form,
        
    }
    return render(request, 'refunds/refund_order.html', context=context)

@login_required
def add_to_refund(request, id):
    item = get_object_or_404(OrderItem, id=id)
    order_id =request.session['refund_order']
    ordered_order = Order.objects.get(id = order_id)
    code = ordered_order.get_code()
    Order_qs = RefundOrder.objects.filter(code = code)
    if Order_qs.exists():
        order = Order_qs[0]
        initial_quantity = item.quantity
        order_id_in_ordered_items = order.code
        return_item, created = RefundOrderItem.objects.get_or_create(order_id = order_id_in_ordered_items,initial_quantity =initial_quantity, item=item, user = request.user)
        #check if the order item is in the order
        if order.refunded_items.filter(item_id = item.id).exists():
            if item.quantity > 0:
                return_item.return_quantity +=1
                return_item.save()
                item.save()
        else:
            if item.quantity > 0:
                return_item.return_quantity = 1
                order.refunded_items.add(return_item)
                return_item.order_id = order.code
                return_item.save()
                item.save()
        return redirect('/pos/refund_order/'+ str(order_id))
    else:
        messages.info(request, "No Refund order is opened. Please open the refund order..")
    return redirect('/pos/refund_order/'+ str(order_id))

@login_required
def create_refund_order(request):
    order_id =request.session['refund_order']
    Order_qs = Order.objects.filter(id = order_id)
    print(Order_qs)
    if Order_qs.exists():
        order = Order_qs[0]
        order_id_code = order.get_code()
        ordered_total_cost = order.order_total_cost
        refund_order, created = RefundOrder.objects.get_or_create(order_id = order, code = order_id_code, ordered_total_cost = ordered_total_cost, user = request.user)
        return redirect('/pos/refund_order/'+ str(order.id))  
    else:
        return redirect('/pos/refund_order/'+ str(order.id))

def get_items_in_refund_order(order):
    order_id = order.get_code
    items_in_order = RefundOrderItem.objects.filter(order_id = order_id)
    return items_in_order

@login_required
def cancel_refund_order(request, id):
    refund_id = id
    print(refund_id)
    order_id =request.session['refund_order']
    Order_qs = RefundOrder.objects.filter(id = refund_id)
    print(Order_qs)
    if Order_qs.exists():
        Order_qs.delete()
        return redirect('/pos/refund_order/'+ str(order_id))
    else:
        order_id =request.session['refund_order']
        return redirect('/pos/refund_order/'+ str(order_id))

def get_items_in_refund_order(order):
    order_id = order.get_code
    items_in_order = RefundOrderItem.objects.filter(order_id = order_id)
    return items_in_order

@login_required
def remove_single_item_refund_order(request, id):
    item = get_object_or_404(OrderItem, id=id)
    order_id =request.session['refund_order']
    ordered_order = Order.objects.get(id = order_id)
    code = ordered_order.get_code()
    Order_qs = RefundOrder.objects.filter(code = code)
    order_id_in_ordered_items = ordered_order.get_code()
    if Order_qs.exists():
        order = Order_qs[0]
        if order.refunded_items.filter(item_id = item.id).exists():
            order_item = RefundOrderItem.objects.filter(order_id = order_id_in_ordered_items)[0]
            if order_item.return_quantity >1:
                order_item.return_quantity -=1
                order_item.save()
                item.save()
            elif order_item.return_quantity == 1:
                order_item.return_quantity -=1
                order_item.delete()
                item.save()
            return  redirect('/pos/refund_order/'+ str(order_id))
        else:
            return  redirect('/pos/refund_order/'+ str(order_id))
    else:
        messages.info(request, "Item not in order")
    # return redirect('/pos/personal_order_list/'+ str(order.id))
    return  redirect('/pos/refund_order/'+ str(order_id))


def refund_payment(request):
    form = AddRefundPaymentForm(request.POST or None)
    if request.method == "POST":
        order_id =request.session['refund_order']
        Order_qs = Order.objects.filter(id = order_id)
        
        try:
            if form.is_valid():
                order = Order_qs[0]
                order_id_code = order.get_code()
                refund_order = RefundOrder.objects.get(code = order_id_code)
                print(refund_order.code)
            
                refund_amount = form.cleaned_data.get('refund_amount')
                payment_mode = request.POST.get('payment_mode')
                refund_payment = RefundPayment()
                refund_payment.payment_mode = payment_mode
                refund_payment.refund_amount = refund_amount
                refund_payment.order_id = order.get_code()
                
                if str(payment_mode).lower() == str('Cash').lower():
                    reference = 'CASH'
                    # payment.payment_mode = reference
                    refund_payment.reference = reference
                elif str(payment_mode).lower() == str('Bank').lower():
                    reference = form.cleaned_data.get('reference') 
                    # payment.payment_mode = reference
                    refund_payment.reference = reference
                else:
                    reference = form.cleaned_data.get('reference') 
                    refund_payment.reference = reference
                refund_payment.save()
                refund_order.payments.add(refund_payment)
                refund_order.payment_reference = reference
                refund_order.save()
                order = Order.objects.get(id = order_id)
            return redirect('/pos/refund_order/'+ str(order_id))
        except ObjectDoesNotExist:
            messages.info(request, "You do not have an active order")
            request.session['refund_order'] = order.id
            return redirect('/pos/refund_order/'+ str(order.id))
        return None

    