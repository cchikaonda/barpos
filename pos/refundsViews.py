from django.shortcuts import render,redirect, get_object_or_404
from inventory.models import ItemCategory, Unit, Item, Supplier
from pos.models import Customer, LayByOrders, OrderItem, Order, Payment, RefundOrder, RefundOrderItem, RefundPayment
from django.contrib import messages
from constance import config
from django.utils import timezone
from datetime import date, timedelta, datetime
from django.core.exceptions import ObjectDoesNotExist
from pos.forms import AddPaymentForm, CashPaymentForm, SearchForm, AddCustomerForm, AddLayByPaymentForm, AddRefundPaymentForm, ReasonForRefund, RestockItemForm
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
    refunded_orders = RefundOrder.objects.all()
    sum_refund_items_total = 0.0

    for refunded_order in refunded_orders:
        sum_refund_items_total += refunded_order.total_refunded_amount
    
    context = {
        'refunded_orders':refunded_orders,
        'sum_refund_items_total':sum_refund_items_total,
    }
    return render(request, 'refunds/refunds_list.html', context=context)

@login_required
def refund_order(request, id):
    paid_order = get_object_or_404(Order,id=id)
    request.session['refund_order'] = paid_order.id
    code = paid_order.get_code()
    refund_order = RefundOrder.objects.filter(code = code)
    restock = RestockItemForm()

    if refund_order.exists():
        order = refund_order[0]
        refund_order = RefundOrder.objects.get(code = order.code)
        refund_total_amount = refund_order.balance_to_refund
        refund_order_items = get_items_in_refund_order(order)
        
        refund_order = RefundOrder.objects.get(code = code)

        refund_payment_form = AddRefundPaymentForm(initial={'refund_amount': refund_total_amount})
        reason_for_refund_form = ReasonForRefund()
        context = {
            'refund_order':refund_order,
            'paid_order':paid_order,
            'refund_order_items':refund_order_items,
            'refund_payment_form':refund_payment_form,
            'reason_for_refund_form':reason_for_refund_form,
            'restock':restock,
        }
        return render(request, 'refunds/refund_order.html', context=context)
    else:
        context = {
        'refund_order':refund_order,
        'paid_order':paid_order,
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
                return_item.return_items_total_cost = return_item.return_amount
                return_item.save()
                item.save()
        else:
            if item.quantity > 0:
                return_item.return_quantity = 1
                order.refunded_items.add(return_item)
                return_item.order_id = order.code
                return_item.return_items_total_cost = return_item.return_amount
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
    if Order_qs.exists():
        order = Order_qs[0]
        order_id_code = order.get_code()
        ordered_total_cost = order.order_total_cost
        refund_order, created = RefundOrder.objects.get_or_create(order_id = order, code = order_id_code, ordered_total_cost = ordered_total_cost, user = request.user)
        return redirect('/pos/refund_order/'+ str(order.id))  
    else:
        return redirect('/pos/refund_order/'+ str(order.id))

@login_required
def get_items_in_refund_order(order):
    order_id = order.get_code
    items_in_order = RefundOrderItem.objects.filter(order_id = order_id)
    return items_in_order

def get_payments_in_refund_order(order):
    order_id = order.get_code
    payments_in_order = RefundPayment.objects.filter(order_id=order_id)
    return payments_in_order

@login_required
def cancel_refund_order(request, id):
    refund_id = id
    order_id =request.session['refund_order']
    Order_qs = RefundOrder.objects.filter(id = refund_id)
    if Order_qs.exists():
        # Deleting refunded items in order before deleting order
        order = RefundOrder.objects.get(id = refund_id)
        refund_order_items = get_items_in_refund_order(order)
        for each_item in refund_order_items:
            each_item.delete()

        refund_order_payments = get_payments_in_refund_order(order)
        for each_payment in refund_order_payments:
            each_payment.delete()
        order.save()
        Order_qs.delete()
        messages.info(request, "Refund order Cancelled Successfully")
        return redirect('/pos/refund_order/'+ str(order_id))
    else:
        order_id =request.session['refund_order']
        return redirect('/pos/refund_order/'+ str(order_id))

@login_required
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
                order_item.return_items_total_cost = order_item.return_amount
                order_item.save()
                item.save()
            elif order_item.return_quantity == 1:
                order_item.return_quantity -=1
                order_item.return_items_total_cost = order_item.return_amount
                order_item.delete()
                item.save()
            return  redirect('/pos/refund_order/'+ str(order_id))
        else:
            return  redirect('/pos/refund_order/'+ str(order_id))
    else:
        messages.info(request, "Item not in order")
    # return redirect('/pos/personal_order_list/'+ str(order.id))
    return  redirect('/pos/refund_order/'+ str(order_id))

# @login_required
# def refund_payment(request):
#     form = AddRefundPaymentForm(request.POST or None)
#     if request.method == "POST":
#         order_id =request.session['refund_order']
#         Order_qs = Order.objects.filter(id = order_id)
        
#         try:
#             if form.is_valid():
#                 order = Order_qs[0]
#                 order_id_code = order.get_code()
#                 refund_order = RefundOrder.objects.get(code = order_id_code)
#                 print(refund_order.code)
            
#                 refund_amount = form.cleaned_data.get('refund_amount')
#                 payment_mode = request.POST.get('payment_mode')
#                 refund_payment = RefundPayment()
#                 refund_payment.payment_mode = payment_mode
#                 refund_payment.refund_amount = refund_amount
#                 refund_payment.order_id = order.get_code()
                
#                 if str(payment_mode).lower() == str('Cash').lower():
#                     reference = 'CASH'
#                     # payment.payment_mode = reference
#                     refund_payment.reference = reference
#                 elif str(payment_mode).lower() == str('Bank').lower():
#                     reference = form.cleaned_data.get('reference') 
#                     # payment.payment_mode = reference
#                     refund_payment.reference = reference
#                 else:
#                     reference = form.cleaned_data.get('reference') 
#                     refund_payment.reference = reference
#                 refund_payment.save()
#                 refund_order.payments.add(refund_payment)
#                 refund_order.payment_reference = reference
#                 refund_order.save()
#                 order = Order.objects.get(id = order_id)
#             return redirect('/pos/refund_order/'+ str(order_id))
#         except ObjectDoesNotExist:
#             messages.info(request, "You do not have an active order")
#             request.session['refund_order'] = order.id
#             return redirect('/pos/refund_order/'+ str(order.id))
#         return None


@login_required
def refund_payment(request):
    if request.method == 'POST':
        order_id =request.session['refund_order']
        Order_qs = Order.objects.filter(id = order_id)
        form = AddRefundPaymentForm(request.POST)
        if form.is_valid():
            order = Order_qs[0]
            order_id_code = order.get_code()
            refund_order = RefundOrder.objects.get(code = order_id_code)

            
            
            reason_for_refund = request.POST.get('reason_for_refund')
            refund_amount = form.cleaned_data.get('refund_amount')
            payment_mode = request.POST.get('payment_mode')
            refund_payment = RefundPayment()
            refund_payment.payment_mode = payment_mode
            refund_payment.refund_amount = refund_amount
            refund_payment.order_id = order.get_code()
            
            restock = request.POST.get('restock_to_inventory')

            refunded_items = RefundOrderItem.objects.filter(order_id = order_id_code)
            print(refunded_items)

            if restock == 'on':
                for refund_item in refunded_items:
                    refund_item.restock_to_inventory = True
                    item_in_inventory = Item.objects.get(item_name = refund_item.item.item.item_name)
                    item_in_inventory.quantity_at_hand += refund_item.return_quantity
                    item_in_inventory.save()
                    refund_item.save()
            else:
                for refund_item in refunded_items:
                    refund_item.restock_to_inventory = False
                    refund_item.save()
            
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
            refund_order.reason_for_refund = reason_for_refund
            refund_order.save()
            order = Order.objects.get(id = order_id)
            messages.success(request, "Payment Processed!")
        return redirect('/pos/refund_order/'+ str(order_id))
    

def complete_refund(request):
    order_id =request.session['refund_order']
    Order_qs = Order.objects.filter(id = order_id)
    order = Order_qs[0]
    order_id_code = order.get_code()
    refund_order = RefundOrder.objects.get(code = order_id_code)
    refund_order.refunded = True
    refund_order.save()
    messages.success(request, "Refund completed")
    return redirect('refunds_list')
    


    