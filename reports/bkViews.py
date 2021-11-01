from django.shortcuts import render,redirect, get_object_or_404
from rest_framework.serializers import Serializer
from inventory.models import ItemCategory, Unit, Item
from pos.models import Customer, OrderItem, Order, Payment
from django.contrib import messages
from constance import config
from django.utils import timezone
from datetime import date, timedelta, datetime
from django.core.exceptions import ObjectDoesNotExist
from pos.forms import AddCustomerForm
from pos.forms import AddPaymentForm, CashPaymentForm, SearchForm
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.core import serializers
import json
from django.contrib.auth.decorators import login_required
from pos.forms import *


from django.http import HttpResponse
from reports.forms import SearchBetweenTwoDatesForm, DefaultReportsForm
from djmoney.money import Money

from serializers.serializers import UserSerializer, OrderItemSerializer, ItemSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework import viewsets
from rest_framework import permissions
from accounts.templatetags import get_key_from_dictionary
from djmoney.contrib.django_rest_framework import MoneyField
from django.db.models import AutoField,IntegerField,FloatField,ExpressionWrapper, F, DecimalField, Count, Sum


@login_required
def reports_dashboard(request):
    form = SearchBetweenTwoDatesForm()
    default_report_form = DefaultReportsForm()
    ordered_items = OrderItem.objects.filter(ordered = True)
    item_categories = ItemCategory.objects.all().order_by('category_name')
    todays_sales = get_todays_sales()

    yesterdays_sales = get_yesterdays_sales()

    #for report
    item_cat = ItemCategory.objects.all()
    if request.method == "POST":
            from_date = request.POST.get('start_date_time')
            to_date = request.POST.get('end_date_time')

            item_cat_para = request.POST.get('item_categories_option')
            report_period = request.POST.get('report_period')
            
            # print(report_period)
            if report_period != None:
                repo_period = get_report_period(report_period)
                if repo_period == timezone.now().date():
                    print(repo_period)
                    ordered_items = ordered_items.filter(ordered_time__gte = repo_period)
                else:
                    ordered_items = ordered_items.filter(ordered_time__gte = repo_period).filter(ordered_time__lt = timezone.now().date())

            if is_valid_queryparam(from_date):
                ordered_items = ordered_items.filter(ordered_time__gte = from_date)
            
            if is_valid_queryparam(to_date):
                ordered_items = ordered_items.filter(ordered_time__lte = to_date)
            
            ordered_total_sales = get_total_sales_for_each_day(ordered_items) 
            total_ordered_quantity = get_total_quantity_for_each_day(ordered_items) 

            context = {
            'home':'Reports',
            'header':'Reports Dashboard',
            'form':form,
            'default_report_form':default_report_form,
            'ordered_items':ordered_items,
            'ordered_total_sales':ordered_total_sales,
            'total_ordered_quantity':total_ordered_quantity,
            'from_date':from_date,
            'to_date':to_date,
            'item_categories':item_categories,
            'todays_sales':todays_sales,
            'yesterdays_sales':yesterdays_sales,

            }
            return render(request, 'reports_dashboard.html', context)
    else:
        ordered_total_sales = get_total_sales_for_each_day(ordered_items)
        total_ordered_quantity = get_total_quantity_for_each_day(ordered_items)
        context = {
        'home':'Reports',
        'header':'Reports Dashboard',
        'form':form,
        'default_report_form':default_report_form,
        'ordered_items':ordered_items,
        'ordered_total_sales':ordered_total_sales,
        'total_ordered_quantity':total_ordered_quantity,
        'item_categories':item_categories,
        'todays_sales':todays_sales,
        'yesterdays_sales':yesterdays_sales,
        }
        return render(request, 'reports_dashboard.html', context)

def is_valid_report_default_report_period(param):
    return param != '' and param is not None and param != 0

def get_report_period(param):
    if param == None:
        param == 6
    param = int(param)
    if param == 1:
        return timezone.now().date()
    if param == 2:
        return timezone.now().date()-timedelta(days=1)
    elif param == 3:
        return datetime.now()-timedelta(days=7)
    elif param == 4:
        return datetime.now()-timedelta(days=30)
    elif param == 5:
        today = timezone.now().date()
        return today.month
    elif param == 6:
        today = timezone.now().date()
        return today.month - 1
    return timezone.now().date()


def is_valid_item_category(param):
    return param != '' and param is not None and param != 0 and param != 1

def is_valid_queryparam(param):
    return param != '' and param is not None
    
def get_todays_sales():
    today_date = timezone.now().date()
    todays_sales = Order.objects.filter(ordered=True).filter(order_date__gte=today_date)
    todays_total_sales = Money('0.00','MWK')
    for todays_s in todays_sales:
        todays_total_sales += todays_s.order_total_cost
    if todays_total_sales == None:
        return Money('0.00','MWK')
    return todays_total_sales

def get_yesterdays_sales():
    yesterdays_date = timezone.now().date()-timedelta(days=1)
    yesterdays_sales = Order.objects.filter(ordered=True).filter(order_date__gte = yesterdays_date).filter(order_date__lt = timezone.now().date())
    yesterdays_total_sales = Money('0.00','MWK')
    for yestrday_s in yesterdays_sales:
        yesterdays_total_sales += yestrday_s.order_total_cost
    if yesterdays_total_sales == None:
        return Money('0.00','MWK')
    return yesterdays_total_sales


def get_todays_sales_report():
    today_date = timezone.now().date()
    # yesterday = today - datetime().timedelta(days=1)

    todays_sales = Order.objects.filter(ordered=True).filter(order_date__gte=today_date)

    return todays_sales

def get_todays_ordered_items():
    today_date = timezone.now().date()
    todays_sales = Order.objects.filter(ordered=True).filter(order_date__gte=today_date)
    todays_ordered_items = OrderItem.objects.filter(ordered = True).filter(ordered_time__gte = today_date).order_by('ordered_time')
    return todays_ordered_items

def get_all_item_categories():
    return ItemCategory.objects.all().order_by('category_name')

def get_total_sales_for_each_day(todays_ordered_items):
    total_sales = 0
    for todays_ordered_item in todays_ordered_items:
        total_sales += todays_ordered_item.ordered_items_total
    return total_sales

def get_total_quantity_for_each_day(todays_ordered_items):
    total_quantity = 0
    for todays_ordered_item in todays_ordered_items:
        total_quantity += todays_ordered_item.quantity
    return total_quantity



def sales_report(request):
    form = SearchBetweenTwoDatesForm()
    default_report_form = DefaultReportsForm()

    total_items_ordered = 0
    total_vat = Money('0.0', 'MWK')
    total_cost_items_ordered = Money('0.0', 'MWK')

    today = timezone.now().date()
    
    repo_period = get_report_period(1)
    item_categories = ItemCategory.objects.all().order_by('category_name')

    # if request.method == "POST":
    #     from_date = request.POST.get('start_date_time')
    #     to_date = request.POST.get('end_date_time')
    #     item_cat_para = request.POST.get('item_categories_option')
    #     print(item_cat_para)
    #     report_period = request.POST.get('report_period')
    #     if report_period != None:
    #         repo_period = get_report_period(report_period)
    #         if item_cat_para != None:
    #             ordered_items = count_items_in_orders_by_item(repo_period, item_cat_para)
    #         else:
    #             ordered_items = count_items_in_orders_by_item_all_categories(repo_period)
    #     elif from_date != None and to_date !=None: 
    #         ordered_items = count_items_in_orders_by_item_using_range(from_date,to_date, item_cat_para)
    #     elif report_period == None:
    #         if item_cat_para != None:
    #             ordered_items = count_items_in_orders_by_item(today, item_cat_para)
    #         else:
    #             ordered_items = count_items_in_orders_by_item_all_categories(today)
    # ordered_items = count_items_in_orders_by_item_all_categories(today)
            
    # for ordered_items_count in ordered_items:
    #     if ordered_items_count.sum !=None and ordered_items_count.total !=None and ordered_items_count.vat_value:
    #         total_items_ordered += int(ordered_items_count.sum)
    #         total_vat += Money(ordered_items_count.vat_value, 'MWK')
    #         total_cost_items_ordered += Money(ordered_items_count.total, 'MWK')

    # total_vat_iclusive = total_cost_items_ordered + total_vat
    ordered_items = count_items_in_orders_by_item_all_categories(today)

    if request.method == "POST":
        from_date = request.POST.get('start_date_time')
        to_date = request.POST.get('end_date_time')
        item_cat_para = request.POST.get('item_categories_option')
        report_period = request.POST.get('report_period')
        repo_period = get_report_period(report_period) 
        # if from_date != None and to_date !=None: 
        #     ordered_items = count_items_in_orders_by_item_using_range(from_date,to_date, item_cat_para)
        # else:       
        if item_cat_para != None:
            ordered_items = count_items_in_orders_by_item(repo_period, item_cat_para)
        else:
            ordered_items = count_items_in_orders_by_item_all_categories(repo_period)
        
        # elif report_period == None:
        #     if item_cat_para != None:
        #         ordered_items = count_items_in_orders_by_item(today, item_cat_para)
        #     else:
        #         ordered_items = count_items_in_orders_by_item_all_categories(today)
        
            
    for ordered_items_count in ordered_items:
        if ordered_items_count.sum !=None and ordered_items_count.total !=None and ordered_items_count.vat_value:
            total_items_ordered += int(ordered_items_count.sum)
            total_vat += Money(ordered_items_count.vat_value, 'MWK')
            total_cost_items_ordered += Money(ordered_items_count.total, 'MWK')

    total_vat_iclusive = total_cost_items_ordered + total_vat

    context = {
        "item_categories":item_categories,
        "default_report_form":default_report_form,
        "form":form,
        "ordered_items":ordered_items,
        "total_items_ordered":total_items_ordered,
        "total_cost_items_ordered":total_cost_items_ordered,
        "total_vat":total_vat,
        "total_vat_iclusive":total_vat_iclusive,
    }
    # return render(request, 'reports_dashboard.html',context)
    return render(request, 'sales_report.html',context)

def get_item_names_in_orders():
    ordered_items = OrderItem.objects.order_by().values('item__item_name').filter(ordered = True).distinct()
    return ordered_items



def count_items_in_orders_by_item(repo_period, category):
    category_id = category
    report_p = repo_period
    print(category_id)
    print(repo_period)
    vat = vat_rate()
    if category_id != None:
        return Item.objects.filter(category__category_name = category_id).filter(orderitem__ordered_time__gte = report_p).annotate(sum=Sum('orderitem__quantity')).annotate(total = Sum(F('orderitem__quantity')*F('orderitem__item__price'), output_field = FloatField())).annotate(default_item_price = Sum(F('price')*1)).annotate(item_price = Sum(F('orderitem__item__price')*1)).annotate(vat_value = Sum(F('orderitem__quantity')*F('orderitem__item__price')*vat, output_field = FloatField())).annotate(tota_vat_inclusive = Sum((F('orderitem__quantity')*F('orderitem__item__price')*vat) + (F('orderitem__quantity')*F('orderitem__item__price')), output_field = FloatField()))
    else:
        return Item.objects.filter(orderitem__ordered_time__gte = report_p).annotate(sum=Sum('orderitem__quantity')).annotate(total = Sum(F('orderitem__quantity')*F('orderitem__item__price'), output_field = FloatField())).annotate(default_item_price = Sum(F('price')*1)).annotate(item_price = Sum(F('orderitem__item__price')*1)).annotate(vat_value = Sum(F('orderitem__quantity')*F('orderitem__item__price')*vat, output_field = FloatField())).annotate(tota_vat_inclusive = Sum((F('orderitem__quantity')*F('orderitem__item__price')*vat) + (F('orderitem__quantity')*F('orderitem__item__price')), output_field = FloatField()))

def count_items_in_orders_by_item_all_categories(repo_period):
    report_p = repo_period
    print(report_p)
    vat = vat_rate()
    return Item.objects.filter(orderitem__ordered_time__lte = report_p).annotate(sum=Sum('orderitem__quantity')).annotate(total = Sum(F('orderitem__quantity')*F('orderitem__item__price'), output_field = FloatField())).annotate(default_item_price = Sum(F('price')*1)).annotate(item_price = Sum(F('orderitem__item__price')*1)).annotate(vat_value = Sum(F('orderitem__quantity')*F('orderitem__item__price')*vat, output_field = FloatField())).annotate(tota_vat_inclusive = Sum((F('orderitem__quantity')*F('orderitem__item__price')*vat) + (F('orderitem__quantity')*F('orderitem__item__price')), output_field = FloatField()))

     

def count_items_in_orders_by_item_using_range(from_date, to_date, category_id):
    from_d = from_date
    to_d = to_date
    vat = vat_rate()
    if category_id !=None:
        ordered_items_count = Item.objects.filter(category__id = category_id).filter(orderitem__ordered_time__range = [from_d, to_d]).annotate(sum=Sum('orderitem__quantity')).annotate(total = Sum(F('orderitem__quantity')*F('orderitem__item__price'), output_field = FloatField())).annotate(default_item_price = Sum(F('price')*1)).annotate(item_price = Sum(F('orderitem__item__price')*1)).annotate(vat_value = Sum(F('orderitem__quantity')*F('orderitem__item__price')*vat, output_field = FloatField())).annotate(tota_vat_inclusive = Sum((F('orderitem__quantity')*F('orderitem__item__price')*vat) + (F('orderitem__quantity')*F('orderitem__item__price')), output_field = FloatField()))
    ordered_items_count = Item.objects.filter(orderitem__ordered_time__range = [from_d, to_d]).annotate(sum=Sum('orderitem__quantity')).annotate(total = Sum(F('orderitem__quantity')*F('orderitem__item__price'), output_field = FloatField())).annotate(default_item_price = Sum(F('price')*1)).annotate(item_price = Sum(F('orderitem__item__price')*1)).annotate(vat_value = Sum(F('orderitem__quantity')*F('orderitem__item__price')*vat, output_field = FloatField())).annotate(tota_vat_inclusive = Sum((F('orderitem__quantity')*F('orderitem__item__price')*vat) + (F('orderitem__quantity')*F('orderitem__item__price')), output_field = FloatField()))
    return ordered_items_count

def vat_rate():
    return float(config.TAX_NAME)/100.00

def sales_report_data(request):
    items = OrderItem.objects.all()
    selialised_items = OrderItemSerializer(items, many=True)
    return JsonResponse(selialised_items.data,safe=False)

