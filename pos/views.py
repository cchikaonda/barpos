from django.shortcuts import render,redirect, get_object_or_404
from inventory.models import ItemCategory, Unit, Item, Supplier
from pos.models import Customer, LayByOrders, OrderItem, Order, Payment, RefundOrder, SessionTime, OpeningQuantity
from django.contrib import messages
from constance import config
from django.utils import timezone
from datetime import date, timedelta, datetime
from django.core.exceptions import ObjectDoesNotExist
from pos.forms import AddPaymentForm, CashPaymentForm, SearchForm, AddCustomerForm, AddLayByPaymentForm, OrderTypeForm, RefundOrderItemForm
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.core import serializers
import json
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from accounts.admin import CustomConfigForm
from epsilonpos import settings
import time
from djmoney.money import Money
from django.template.loader import render_to_string


from django.http import HttpResponse

import qrcode
import qrcode.image.svg
from io import BytesIO
from django.db.models.query import *
from datetime import datetime

@login_required
def index(request):
    context = {}
    #generating QR Code
    if request.method == "POST":
        factory = qrcode.image.svg.SvgImage
        img = qrcode.make(request.POST.get("qr_text",""), image_factory=factory, box_size=20)
        stream = BytesIO()
        img.save(stream)
        context["svg"] = stream.getvalue().decode()
    return render(request, 'index.html', context=context)

@login_required
def pos_dashboard(request):   
    if 'opened_order' in request.session:
        del request.session['opened_order']
    if config.QUICK_SALE == 'yes':
        return redirect('add_customer_to_order')
    customers = Customer.objects.all()
    form = AddCustomerForm()
    unpaid_orders = Order.objects.filter(user = request.user, ordered = False)
    count_my_customers = Order.objects.filter(user = request.user, ordered = False).count()
    


    sum_unpaid_orders = 0.0
    
    for unpaid_order in unpaid_orders:
        sum_unpaid_orders += unpaid_order.order_total_due()

    context = {
        'home':'Home',
        'header':'Pos Dashboard',
        'customers':customers,
        'form':form,
        'unpaid_orders':unpaid_orders,
        'config':config,
        'sum_unpaid_orders':sum_unpaid_orders,
        'count_my_customers':count_my_customers,
        }
    return render(request, 'pos_dashboard.html', context)

@login_required
def add_customer_to_order(request):
    # order_date = timezone.now()
    if request.method == "POST":
        selected_customer = request.POST.get('customer_name')
        customer = Customer.objects.get(name=selected_customer)
        try: 
            #check if there is already order for the customer
            check_order = Order.objects.get(user = request.user, customer = customer, ordered = False)
            if check_order:
                return redirect('/pos/personal_order_list/'+ str(check_order.id))
        except ObjectDoesNotExist:
            order = Order.objects.create(user = request.user, customer = customer)
            order.code = order.get_code()
            order.save()
        return redirect('/pos/personal_order_list/'+ str(order.id))
    else:
        customer = Customer.objects.get(id=1)
        try: 
            #check if there is already order for the customer
            check_order = Order.objects.get(user = request.user, customer = customer, ordered = False)
            if check_order:
                return redirect('/pos/personal_order_list/'+ str(check_order.id))  
        except ObjectDoesNotExist:
            order = Order.objects.create(user = request.user, customer=customer)
            order.code = order.get_code()
            order.save()
            return redirect('/pos/personal_order_list/'+ str(order.id))



@login_required
def add_new_customer_from_pos_dash(request):
    form = AddCustomerForm(request.POST or None)
    if request.method == "POST":
        try:
            if form.is_valid():
                form.save()
                messages.success(request, "New Customer is Added!")
            return HttpResponseRedirect("pos_dashboard")
        except ObjectDoesNotExist:
            messages.warning(request, "You do not have an active order")
            return redirect("pos_dashboard")
        return None


@login_required
def add_payment(request):
    form = AddPaymentForm(request.POST or None)
    if request.method == "POST":
        order_id =request.session['opened_order']
        order = Order.objects.get(id = order_id, user = request.user, ordered=False)
        try:
            if form.is_valid():
                paid_amount = form.cleaned_data.get('paid_amount')
                payment_mode = request.POST.get('payment_mode')
                
                

                customer = order.customer
                order_type = order.order_type
                payment = Payment()
                payment.payment_mode = payment_mode
                payment.order_type = order_type
                payment.paid_amount = paid_amount
                payment.customer = customer
                payment.order_id = order.get_code()
                
                
                
                
                reference2 = form.cleaned_data.get('reference')
                payment_mode_here = get_bill_based_on_payment_mode(reference2)
                print(payment_mode_here)
                payment.save()
                order.payments.add(payment)
                order.save()
                order = Order.objects.get(id = order_id)
                request.session['opened_order'] = order.id
                messages.success(request, "Payment Added! " + str(paid_amount))
            return redirect('/pos/personal_order_list/'+ str(order.id))
        except ObjectDoesNotExist:
            messages.info(request, "You do not have an active order")
            order = Order.objects.get(user = request.user, ordered = False)
            request.session['opened_order'] = order.id
            return redirect('/pos/personal_order_list/'+ str(order.id))
        return None

@login_required
def change_order_type(request):
    form = OrderTypeForm(request.POST or None)
    if request.method == "POST":
        order_id =request.session['opened_order']
        order = Order.objects.filter(id = order_id)
        try:
            if form.is_valid():
                order_type = form.cleaned_data.get('order_type')
                order.update(order_type = order_type)
                order = Order.objects.get(id = order_id, user = request.user, ordered = False)
                order_id = order.get_code()

                order_payments = Payment.objects.filter(order_id =order_id)
                for order_payment in order_payments:
                    order_payment.order_type = order_type
                    order_payment.save()
                # request.session['opened_order'] = order.id
            return redirect('/pos/personal_order_list/'+ str(order.id))
        except ObjectDoesNotExist:
            messages.info(request, "You do not have an active order")
            # request.session['opened_order'] = order.id
            return redirect('/pos/personal_order_list/'+ str(order.id))
        return None



@login_required
def complete_order_only(order, request):
    # order_id =request.session['opened_order']
    order_id = order.id
    order = Order.objects.get(id = order_id, user = request.user, ordered=False)
    order.customer.total_orders +=1
    order.customer.save()
    order.order_total_cost = order.order_total_due()
    order_item = OrderItem.objects.filter(user = request.user, ordered = False, customer = order.customer)
    for order_item in order_item:
        order_item.ordered_item_price = order_item.price
        order_item.ordered_items_total = order_item.get_total_amount
        order_item.ordered = True
        order_item.save()
    order.ordered = True
    order.vat_p = order.vat_rate
    order.vat_cost = order.get_vat_value
    order.save()
    request.session['opened_order'] = order.id


@login_required
def complete_order(request):
    order_id =request.session['opened_order']
    order = Order.objects.get(id = order_id)
    order.customer.total_orders +=1
    order.customer.save()
    order.order_total_cost = order.order_total_due()
    order_item = OrderItem.objects.filter(user = request.user, ordered = False, customer = order.customer)
    for order_item in order_item:
        order_item.ordered_item_price = order_item.price
        order_item.ordered_items_total = order_item.get_total_amount
        order_item.ordered = True
        order_item.save()
    order.ordered = True
    order.vat_p = order.vat_rate
    order.save()
    return redirect("pos_dashboard")

@login_required
def customers_list(request):
    payment_options = AddPaymentForm()
    all_orders = Order.objects.all()
    unsettled_orders = Order.objects.filter(user=request.user, ordered = False)
    settled_orders = Order.objects.filter(user=request.user, ordered = True)
    Order_qs = Order.objects.filter(user=request.user, ordered= False)
    if Order_qs.exists():
        current_order = Order_qs[0]
        # if current_order.active == True:
        #     current_order.active = False
        current_order.save()

    customers = Customer.objects.all()
    customers_count = customers.count()
    orders = Order.objects.all()
    orders_count = orders.count()
    settled_orders_count = settled_orders.count()
    unsettled_orders_count = unsettled_orders.count()
    all_orders_count = all_orders.count()
    context = {
        'customers':customers,
        'orders':orders,
        'config':config,
        'all_orders':all_orders,
        'settled_orders':settled_orders,
        'unsettled_orders':unsettled_orders,
        'customers_count':customers_count,
        'settled_orders_count':settled_orders_count,
        'unsettled_orders_count':unsettled_orders_count,
        'all_orders_count':all_orders_count,
        'header':'Bills',
        'home':'Home',
        'payment_options':payment_options,
        'config':config,
    }
    return render(request, 'customers_list.html', context)

@login_required
def personal_order_list(request, id):
    item_search_form = SearchForm()
    order_type_form = OrderTypeForm(initial={"order_type":'Cash'})
    cash_payment_form = AddPaymentForm(initial={"paid_amount":[''],})
    mpamba_payment_form = AddPaymentForm(initial={"paid_amount":[''],"payment_mode":'Mpamba',})
    airtel_payment_form = AddPaymentForm(initial={"paid_amount":[''],"payment_mode":'Airtel Money',})
    bank_payment_form = AddPaymentForm(initial={"paid_amount":[''],"payment_mode":'Bank',})

    order = get_object_or_404(Order,id=id)

    total_paid_amount = order.total_paid_amount()
    order_total_due = order.order_total_due()
    
    request.session['opened_order'] = order.id
  
    unsettled_orders = Order.objects.filter(user=request.user, ordered = False, order_total_cost__gt = 0.0)

    save_order(order, request)
    items_in_order = get_items_in_order(order)

    item_categories = ItemCategory.get_all_item_categories().annotate(item_in_category_count=Count('item'))

    items = None
    item_cat_id = request.GET.get('category')
    if item_cat_id:
        items = Item.get_all_items_by_category_id(item_cat_id).filter(active=True).filter(quantity_at_hand__gt=0)
        item_count = items.count()
    else:
        items = Item.get_all_items().filter(active=True).filter(quantity_at_hand__gt=0)
        item_count = items.count()
    all_items_count = Item.objects.count()
    category = ItemCategory.objects.filter(id=item_cat_id)


    query = request.POST.get("barcode", None)
    if query is not None:
        # items = (items.filter(barcode__startswith  = query) | items.filter(item_name__startswith  = query))|items.filter(item_name__icontains = query)
        # if items.exists:
        item_exist = Item.objects.filter(barcode = query)
        if item_exist.exists():
            item = Item.objects.get(barcode = query)
            slug = item.slug
            add_to_cart(request, slug)
        else:
            messages.error(request, "Item with barcode " + query + " is not found")
            return redirect('/pos/personal_order_list/'+ str(order.id))
            
    this_order_payments = Payment.objects.filter(order_id = order.get_code()).order_by('-created_at')
    

    context = {
        'order':order,
        'item_categories':item_categories,
        'items':items,
        'item_count':item_count,
        'all_items_count':all_items_count,
        'config':config,
        'items_in_order':items_in_order,
        'home':'Home',
        'header':'Order' + ' ' + str(order.id),
        'this_order_payments':this_order_payments,
        
        'category':category,
        'unsettled_orders':unsettled_orders,
        'item_search_form':item_search_form,
        'config':config,
        'order_type_form':order_type_form,

        'total_paid_amount':total_paid_amount,
        'order_total_due':order_total_due,
        'cash_payment_form':cash_payment_form,
        'mpamba_payment_form':mpamba_payment_form,
        'airtel_payment_form':airtel_payment_form,
        'bank_payment_form':bank_payment_form,
    }
    return render(request, 'personal_order_list.html',context)

def get_bill_based_on_payment_mode(payment_mode):
        payment_mode = payment_mode
        if payment_mode == 'Airtel Money':
            return get_airtel_money_bill()
        elif payment_mode == 'Mpamba':
            return get_mpamba_bill()
def get_mpamba_bill():
    pass
def get_airtel_money_bill():
    pass
    

@login_required
def save_order(order, request):
    order.order_total_cost = order.order_total_due()
    order.save()
    return order

@login_required
def save_bill(request):
    order_id = request.session['opened_order']
    order = Order.objects.get(id = order_id, user = request.user, ordered=False)
    save_order(order, request)
    return redirect('pos_dashboard')

@login_required
def save_bill_and_print_receipt(request):
    order_id =request.session['opened_order']
    order = Order.objects.get(id = order_id, user = request.user, ordered=False)
    # order.active = False
    save_order(order, request)
    return redirect('pos_dashboard')


@login_required
def get_items_in_order(order):
    items_in_order = OrderItem.objects.filter(order_id = order.get_code(), ordered=False, customer=order.customer)
    # items_in_order = order.items.all
    return items_in_order


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_id =request.session['opened_order']
    Order_qs = Order.objects.filter(id = order_id)
    if Order_qs.exists():
        order = Order_qs[0]
        customer = order.customer
        order_id_in_ordered_items = order.get_code()
        print("getting order items....")
        # time.sleep(5)
        order_item, created = OrderItem.objects.get_or_create(order_id = order_id_in_ordered_items, item=item, user = request.user, ordered = False, customer=customer)
        #check if the order item is in the order
        if order.items.filter(item__slug = item.slug).exists():
            if item.quantity_at_hand > 0:
                item.quantity_at_hand -=1
                order_item.quantity +=1
                order_item.customer = order.customer
                order_item.save()
                item.save()
        else:
            if item.quantity_at_hand > 0:
                order_item.quantity = 1
                order.items.add(order_item)
                order_item.customer = order.customer
                order_item.order_id = order.get_code()
                order_item.save()
                item.quantity_at_hand -=1
                item.save()
    else:
        messages.info(request, "Item not in order")
    return redirect('/pos/personal_order_list/'+ str(order_id))

@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_id =request.session['opened_order']
    # Order_qs = Order.objects.filter(user=request.user, ordered= False, active=True)
    Order_qs = Order.objects.filter(id = order_id)

    if Order_qs.exists():
        order = Order_qs[0]
        order = Order_qs[0]
        customer = order.customer
        # order_id = order.order_id
        order_id_in_ordered_items = order.get_code()
        #check if the order item is in the order
        if order.items.filter(item__slug = item.slug).exists():
            order_item = OrderItem.objects.filter(order_id = order_id_in_ordered_items, item = item, user = request.user, ordered = False, customer=customer)[0]
            order_item.ordered = True
            order.items.remove(order_item)
            item.quantity_at_hand += order_item.quantity
            order_item.delete()
            item.save()
            # order_item.save()
        else:
        # add a message saying the user doesnt have an order
            messages.info(request, "This Item is not in Cart!")
            return redirect ('/pos/personal_order_list/'+ str(order.id))
    else:
        messages.info(request, "Item not in order")
    # return redirect('/pos/personal_order_list/'+ str(order.id))
    return redirect('/pos/personal_order_list/'+ str(order_id))

@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_id =request.session['opened_order']
    # Order_qs = Order.objects.filter(user=request.user, ordered= False, active=True)
    Order_qs = Order.objects.filter(id = order_id)
    if Order_qs.exists():
        order = Order_qs[0]
        customer = order.customer
        #check if the order item is in the order
        if order.items.filter(item__slug = item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user = request.user, ordered = False, customer=customer)[0]
            if order_item.quantity >1:
                order_item.quantity -=1
                item.quantity_at_hand +=1
                order_item.save()
                item.save()
            elif order_item.quantity == 1:
                order_item.quantity -=1
                item.quantity_at_hand +=1
                order_item.delete()
                item.save()
            return redirect('/pos/personal_order_list/'+ str(order.id))
        else:
            return redirect('/pos/personal_order_list/'+ str(order.id))
    else:
        messages.info(request, "Item not in order")
    # return redirect('/pos/personal_order_list/'+ str(order.id))
    return redirect('/pos/personal_order_list/'+ str(order_id))

def remove_payment(request, id):
    payment = get_object_or_404(Payment, id=id)
    order_id = Order.objects.get(code = str(payment.order_id))
    payment.delete()
    return redirect('/pos/personal_order_list/'+ str(order_id.id))

@login_required
def receipt(request):
    now = datetime.now()

    order_id =request.session['opened_order']
    order = Order.objects.get(id = order_id, user = request.user, ordered=False)

    q = {" Order Number: " + str(order_id), " Customer:" + str(order.customer) + " Cel: " + str(order.customer.phone_number)}

    factory = qrcode.image.svg.SvgImage
    img = qrcode.make(q, image_factory=factory, box_size=5)
    stream = BytesIO()
    img.save(stream)
    svg = stream.getvalue().decode()

    # complete_order_only(order, request)
    
    request.session['opened_order'] = order.id

    context = {
        'config':config,
        'order':order,
        'svg':svg,
        'now':now,
    }
    return render(request, 'receipt.html', context)

@login_required
def final_receipt(request):
    now = datetime.now()

    order_id =request.session['opened_order']
    order = Order.objects.get(id = order_id, user = request.user, ordered=False)

    q = {" Order Number: " + str(order_id), " Customer:" + str(order.customer) + " Cel: " + str(order.customer.phone_number)}

    factory = qrcode.image.svg.SvgImage
    img = qrcode.make(q, image_factory=factory, box_size=5)
    stream = BytesIO()
    img.save(stream)
    svg = stream.getvalue().decode()

    # complete_order_only(order, request)
    
    request.session['opened_order'] = order.id

    context = {
        'config':config,
        'order':order,
        'svg':svg,
        'now':now,
    }
    return render(request, 'final_receipt.html', context)

@login_required
def print_receipt_only(request):
    now = datetime.now()

    order_id =request.session['opened_order']
    order = Order.objects.get(id = order_id, user = request.user, ordered=False)

    q = {" Order Number: " + str(order_id), " Customer:" + str(order.customer) + " Cel: " + str(order.customer.phone_number)}

    factory = qrcode.image.svg.SvgImage
    img = qrcode.make(q, image_factory=factory, box_size=5)
    stream = BytesIO()
    img.save(stream)
    svg = stream.getvalue().decode()
    request.session['opened_order'] = order.id
    context = {
        'config':config,
        'order':order,
        'svg':svg,
        'now':now,
    }
    return render(request, 'receipt.html', context)

@login_required
def print_receipt_from_modal(request, id):
    now = datetime.now()

    order_id = id
    order = Order.objects.get(id = order_id)

    q = {" Order Number: " + str(order_id), " Customer:" + str(order.customer) + " Cel: " + str(order.customer.phone_number)}

    factory = qrcode.image.svg.SvgImage
    img = qrcode.make(q, image_factory=factory, box_size=5)
    stream = BytesIO()
    img.save(stream)
    svg = stream.getvalue().decode()
    request.session['opened_order'] = order.id
    context = {
        'config':config,
        'order':order,
        'svg':svg,
        'now':now,
    }
    return render(request, 'receipt.html', context)

@login_required
def load_orders(request):
    unpaid_orders = Order.objects.filter(ordered=False)
    context = {
        'unpaid_orders':unpaid_orders,
        'config':config,
    }
    return render(request, 'unpaid_orders.html', context)

# WE don't need csrf_token when using Ajax
@csrf_exempt
def load_orders(request):
   
    # Getting all unpaid_orders from Order model based on ordered False/True
    unpaid_orders = Order.objects.filter(ordered=False)

    # Only Passing Customer Name order Total Cost  Only
    list_data = []

    for unpaid_order in unpaid_orders:
        data_small={"id":unpaid_order.id, "customer":unpaid_order.customer +" "+unpaid_order.order_total_cost}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


@login_required
def incident_list(request):
    incidents = Order.objects.all().order_by("-opened_at")[:10]
    return render(request, "incident-list.html", locals())

# View for the modal
@login_required
def view_order_items(request, id):
    order = get_object_or_404(Order, id=id)
    context = {
        'order':order,
        'config':config,
    }
    return render(request, 'view_order_items.html', context)

@login_required
def view_my_orders(request):
    customers = Customer.objects.all()
    paid_orders = Order.objects.filter(user = request.user, ordered = True)
    unpaid_orders = Order.objects.filter(user = request.user, ordered = False)
    count_my_customers = Order.objects.filter(user = request.user, ordered = False).count()


    sum_unpaid_orders = 0.0
    sum_paid_orders = 0.0

    for paid_order in paid_orders:
        sum_paid_orders += paid_order.order_total_due()
    for unpaid_order in unpaid_orders:
        sum_unpaid_orders += unpaid_order.order_total_due()

    context = {
        'customers':customers,
        'config':config,
        'paid_orders':paid_orders,
        'unpaid_orders':unpaid_orders,
        'sum_unpaid_orders':sum_unpaid_orders,
        'sum_paid_orders':sum_paid_orders,
        'count_my_customers':count_my_customers,


    }
    return render(request, "view_my_orders.html", context)

@login_required
def view_all_orders(request):
    paid_orders = Order.objects.filter(ordered = True)
    refund_orders = RefundOrder.objects.all()
    unpaid_orders = Order.objects.filter(ordered = False)
    # count_my_customers = Order.objects.filter(ordered = False).count()

    # orders_with_refunds = Order.objects.filter(refundorder__in = refund_orders)

    
    sum_unpaid_orders = 0.0
    sum_paid_orders = 0.0

    for paid_order in paid_orders:
        sum_paid_orders += paid_order.order_total_due()
    for unpaid_order in unpaid_orders:
        sum_unpaid_orders += unpaid_order.order_total_due()

    context = {
        'refund_orders':refund_orders,
        'config':config,
        'paid_orders':paid_orders,
        'unpaid_orders':unpaid_orders,
        'sum_unpaid_orders':sum_unpaid_orders,
        'sum_paid_orders':sum_paid_orders,
    }
    return render(request, "view_all_orders.html", context)

@login_required
def supplier_list_pos(request):
    suppliers = Supplier.objects.all()
    context = {
        'suppliers': suppliers,
        'header': 'Manage Suppliers',
        'config':config,
    }
    return render(request, 'suppliers/supplier_list_pos.html', context)

@login_required
def create_new_customer_on_pos_dash(request):
    if request.method == 'POST':
        form = AddCustomerForm(request.POST)
    else:
        form = AddCustomerForm()
    return save_added_customer_on_pos_dash(request, form, 'create_new_customer_on_pos_dash.html')

@login_required
def save_added_customer_on_pos_dash(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            customers = Customer.objects.all()
            data['customer_list'] = render_to_string('pos_dashboard.html', {'customers': customers})
        else:
            data['form_is_valid'] = False
    context = {
        'form': form
    }
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)

@login_required
def customer_list_pos(request):
    customers = Customer.objects.all()
    context = {
        'customers': customers,
        'header': 'Manage customers',
        'config':config,
    }
    return render(request, 'customers/customer_list_pos.html', context)

@login_required
def save_customer_list(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            customers = Customer.objects.all()
            data['customer_list'] = render_to_string('customers/customer_list_2_pos.html', {'customers': customers})
        else:
            data['form_is_valid'] = False
    context = {
        'form': form
    }
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


@login_required
def customer_create_pos(request):
    if request.method == 'POST':
        form = AddCustomerForm(request.POST)
    else:
        form = AddCustomerForm()
    return save_customer_list(request, form, 'customers/customer_create_pos.html')

@login_required
def customer_update_pos(request, id):
    customer = get_object_or_404(Customer, id=id)
    if request.method == 'POST':
        form = AddCustomerForm(request.POST, instance=customer)
    else:
        form = AddCustomerForm(instance=customer)
    return save_customer_list(request, form, 'customers/customer_update_pos.html')

@login_required
def customer_delete_pos(request, id):
    data = dict()
    customer = get_object_or_404(Customer, id=id)
    if request.method == "POST":
        customer.delete()
        data['form_is_valid'] = True
        customers = Customer.objects.all()
        data['customer_list'] = render_to_string('customers/customer_list_2_pos.html', {'customers': customers})
    else:
        context = {'customer': customer}
        data['html_form'] = render_to_string('customers/customer_delete_pos.html', context, request=request)
    return JsonResponse(data)

def clock_in(request):
    clock_in_time = timezone.now()
    SessionTime.objects.create(open_time = clock_in_time )
    session_time = SessionTime.objects.last()
    items = Item.objects.all()
    for item in items:
        opening_quantity = item.quantity_at_hand
        OpeningQuantity.objects.create(item_name = item, opening_quantity = opening_quantity, session_time = session_time)
    messages.success(request, "Clocked in at " + datetime.now().strftime('%H:%M %p') + ' on ' + datetime.now().strftime('%d/%m/%Y'))
    return redirect('system_dashboard')

def clock_out(request):
    session_time = SessionTime.objects.last()
    clock_out = timezone.now()
    session_time.closing_time = clock_out
    items = Item.objects.all()
    for item in items:
        closing_quantity = item.quantity_at_hand
        item_qty = OpeningQuantity.objects.filter(item_name = item).last()
        item_qty.closing_quantity = closing_quantity
        item_qty.save()
    session_time.save()
    messages.success(request, "Clocked out at " + datetime.now().strftime('%H:%M %p') + ' on ' + datetime.now().strftime('%d/%m/%Y'))
    return redirect('system_dashboard')