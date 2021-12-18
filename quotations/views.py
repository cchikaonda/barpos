from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.messages.views import SuccessMessageMixin
from django.views import generic
from django.urls import reverse_lazy
from django.contrib import messages
from django.template.loader import render_to_string
from django.http import JsonResponse
from constance import config
from constance.admin import ConstanceAdmin, ConstanceForm, Config
from django.shortcuts import render,redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from rest_framework.filters import SearchFilter, OrderingFilter

from django.contrib.messages.views import SuccessMessageMixin
import json
import datetime
from django.utils import timezone
import json
from django.http import JsonResponse
from django.contrib.sessions.models import Session
from inventory.models import ItemCategory, Item
from .models import QuotationItem, Quotation
from pos.models import Customer, CustomUser
from inventory.templatetags.inventory_template_tags import cart_item_count
from pos.forms import SearchForm
from pos.forms import AddCustomerForm

def quotation(request):
    current_quotation = Quotation.objects.get(user=request.user, ordered = False)
    context = {
        'config':config,
        'current_quotation':current_quotation,
    }
    return render(request, 'quotations/quotation.html',context )

def quotation_dashboard(request):
    item_cat = ItemCategory.get_all_item_categories()
    customers = Customer.objects.all()

    items = None
    item_cat_id = request.GET.get('category')
    if item_cat_id:
        items = Item.get_all_items_by_category_id(item_cat_id)
    else:
        items = Item.get_all_items()

    try:
        order = Quotation.objects.get(user=request.user, ordered = False)
    except ObjectDoesNotExist:
        order = ""
    
    query = request.GET.get("barcode", None)
    if query is not None:
        items = (items.filter(barcode__startswith  = query) | items.filter(item_name__startswith  = query))|items.filter(item_name__icontains = query)
    
    items_in_order = cart_item_count(user=request.user)

    item_search_form = SearchForm()
   
    customer_form = AddCustomerForm()

    context = {
     'items_in_order':items_in_order,
      'items':items,
      'order':order,
      'item_cat':item_cat,
      'item_search_form':item_search_form,
      'customers':customers,
      'customer_form':customer_form,
      'config':config,
    }
    return render(request, 'quotations/quotation_dashboard.html',context)

def add_to_cart_quotation(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = QuotationItem.objects.get_or_create(item=item, user = request.user, ordered = False)
    Order_qs = Quotation.objects.filter(user=request.user, ordered= False)
    if Order_qs.exists():
        order = Order_qs[0]
        #check if the order item is in the order
        if order.items.filter(item__slug = item.slug).exists():
            order_item.quantity +=1
            order_item.save()
            item.save()
        else:
            order.items.add(order_item)
            item.save()
    else:
        order_date = timezone.now()
        order = Quotation.objects.create(user = request.user, order_date = order_date)
        order.items.add(order_item)
        item.save()
    return redirect('quotation_dashboard')

def remove_from_cart_quotation(request, slug):
    item = get_object_or_404(Item, slug=slug)
    Order_qs = Quotation.objects.filter(user=request.user, ordered= False)

    if Order_qs.exists():
        order = Order_qs[0]
        #check if the order item is in the order
        if order.items.filter(item__slug = item.slug).exists():
            order_item = QuotationItem.objects.filter(item = item, user = request.user, ordered = False)[0]
            order_item.ordered = True
            order.items.remove(order_item)
            order_item.delete()
            item.save()
        else:
        # add a message saying the user doesnt have an order
            messages.info(request, "This Item is not in Cart!")
            return redirect ('quotation_dashboard')
    else:
        messages.info(request, "You do not have an active Order!")
        return redirect ('quotation_dashboard')
    return redirect ('quotation_dashboard')

def remove_single_item_from_cart_quotation(request, slug):
    item = get_object_or_404(Item, slug=slug)
    Order_qs = Quotation.objects.filter(user=request.user, ordered= False)
    if Order_qs.exists():
        order = Order_qs[0]
        #check if the order item is in the order
        if order.items.filter(item__slug = item.slug).exists():
            order_item = QuotationItem.objects.filter(item=item, user = request.user, ordered = False)[0]
            if order_item.quantity >1:
                order_item.quantity -=1
                order_item.save()
                item.save()
            else:
                order.items.remove(order_item)
                item.save()
            return redirect("quotation_dashboard")
        else:
            return redirect("quotation_dashboard")
    else:
        messages.info(request, "You do not have an active order!")
    return redirect('quotation_dashboard')

def suspend_order(request):
    order = Quotation.objects.get(user=request.user, ordered = False)
    orderitems = order.items.all()
    #Making sure that ordered items are un checked to allow new items start form 1 on new order
    for orderitem in orderitems:
        orderitem.ordered = True
        orderitem.save()
    order.delete()
    return redirect('quotation_dashboard')

def complete_quotation(request):
    order_items = QuotationItem.objects.filter(user = request.user, ordered = False)
    for order_item in order_items:
        order_item.ordered_item_price = order_item.price
        order_item.ordered_items_total = order_item.amount
        order_item.ordered = True
        order_item.save()
    order = Quotation.objects.get(user = request.user, ordered = False)
    # order.customer.total_quotations +=1
    order.status = 'Pending'
    order.customer.save()
    order.order_total_cost = order.order_total_due()
    order.vat_cost = order.get_vat_value
    order.vat_p = order.vat_rate
    order.code = order.get_code()
    order.ordered = True
    order.save()
    
    return redirect("quotation_dashboard")

def add_customer_to_quotation(request):
    if request.method == "POST":
        try:
            order = Quotation.objects.get(user = request.user, ordered = False)
            selected_customer = request.POST.get('customer_name')
            order.customer = Customer.objects.get(name=selected_customer)
            order.save()
            return redirect("quotation_dashboard")
        except ObjectDoesNotExist:
            messages.info(request, "You do not have an active order")
            return redirect("quotation_dashboard")
        return None

def change_markup(request):
    if request.method == "POST":
        try:
            order = Quotation.objects.get(user = request.user, ordered = False)
            selected_markup = request.POST.get('markup')
            order.markup = selected_markup
            order.save()
            return redirect("quotation_dashboard")
        except ObjectDoesNotExist:
            messages.info(request, "You do not have an active order")
            return redirect("quotation_dashboard")
        return None
  
def add_expire_date_to_quotation(request):
    if request.method == "POST":
        try:
            order = Quotation.objects.get(user = request.user, ordered = False)
            selected_expire_date = request.POST.get('expire_date')
            order.expire_date = selected_expire_date
            order.save()
            return redirect("quotation_dashboard")
        except ObjectDoesNotExist:
            messages.info(request, "You do not have an active order")
            return redirect("quotation_dashboard")
        return None

def add_customer(request):
    form = AddCustomerForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
        return redirect("quotation_dashboard")

def quotation_summery(request, id):
    current_quotation = get_object_or_404(Quotation, id=id)
    time_now = datetime.datetime.today()
    order_item = QuotationItem.objects.filter(user = request.user, ordered = False)
    for order_item in order_item:
        order_item.ordered = True
        order_item.save()
    context = {
        'current_quotation':current_quotation,
        'time_now':time_now,
        'header': 'Orders',
        'config':config,
    }
    return render(request, 'quotations/quotation_summery.html', context)

@login_required
def quotation_list(request):
    quotations = Quotation.objects.all()
    context = {
    'quotations': quotations,
    'header': 'Manage Quotations',
    'config':config,
    }
    return render(request, 'quotations/quotation_list.html',context)

@login_required
def quotation_update(request, id):
    quotation = get_object_or_404(QuotationItem, id=id)
    if request.method == 'POST':
        form = UpdateQuotationForm(request.POST, instance=quotation)
    else:
        form = UpdateQuotationForm(instance=quotation)
    return save_all_quotations(request, form, 'quotations/quotation_update.html')

@login_required
def quotation_delete(request, id):
    data = dict()
    quotation = get_object_or_404(Quotation, id=id)
    if request.method == "POST":
        quotation.delete()
        data['form_is_valid'] = True
        quotations = Quotation.objects.all()
        data['quotation_list'] = render_to_string('quotations/quotation_list_2.html', {'quotations': quotations})
    else:
        context = {'quotation': quotation}
        data['html_form'] = render_to_string('quotations/quotation_delete.html', context, request=request)
    return JsonResponse(data)

@login_required
def save_all_quotations(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            quotations = Quotation.objects.all()
            data['quotation_list'] = render_to_string('quotations/quotation_list_2.html', {'quotations': quotations})
        else:
            data['form_is_valid'] = False
    context = {
        'form': form
    }
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)

def get_current_users():
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    user_id_list = []
    for session in active_sessions:
        data = session.get_decoded()
        user_id_list.append(data.get('_auth_user_id', None))
    # Query all logged in users based on id list
    return CustomUser.objects.filter(id__in=user_id_list)

def get_items_in_order(request):
    return QuotationItem.objects.filter(user = request.user, ordered = False).count()