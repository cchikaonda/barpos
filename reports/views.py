from django.shortcuts import render,redirect, get_object_or_404
from rest_framework.serializers import Serializer
from inventory.models import ItemCategory, Unit, Item
from pos.models import Customer, OrderItem, Order, Payment
from django.contrib import messages
from constance import config
from django.utils import timezone
from datetime import date, timedelta, datetime, time
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

from djmoney.models.managers import understands_money

@login_required
def reports_dashboard(request):
    form = SearchBetweenTwoDatesForm()
    default_report_form = DefaultReportsForm()
    ordered_items = OrderItem.objects.filter(ordered = True)
    item_categories = ItemCategory.objects.all().order_by('category_name')
    todays_sales = get_todays_sales()

    today = timezone.now().date()

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
                if repo_period == 1:
                    #print(repo_period)
                    ordered_items = ordered_items.filter(ordered_time__lte = today)
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
            'config':config,

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
        'config':config,
        }
        return render(request, 'reports_dashboard.html', context)

def is_valid_report_default_report_period(param):
    return param != '' and param is not None and param != 0

def get_report_period(param):
    if param == None:
        param == 6
    param = int(param)
    if param == 0:
        return 1
    elif param == 1:
        return timezone.now().date()
    elif param == 2:
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
    item_cat = "All Categories"
    report_period = "All Days"

    total_items_ordered = 0
    total_vat = Money('0.0', 'MWK')
    total_cost_items_ordered = Money('0.0', 'MWK')

    today = timezone.now().date()
    
    item_categories = ItemCategory.objects.all().order_by('category_name')

    total_vat_iclusive = total_cost_items_ordered + total_vat
    ordered_items = all_days_sales(0)

    if request.method == "POST":
        item_cat = request.POST.get('item_categories_option')
        period = request.POST.get('report_period')
        report_period = int(period)
        #print(report_period)
        #print(item_cat)
        if report_period == 0:
            ordered_items = all_days_sales(item_cat)
            report_period = "All Days"
        elif report_period == 1:
            ordered_items = today_sales(item_cat)
            report_period = "Today"
        elif report_period == 2:
            ordered_items = yesterday_sales(item_cat)
            report_period = "Yesterday"
        elif report_period == 3:
            ordered_items = last_7_days_sales(item_cat)
            report_period = "Last 7 Days"
        elif report_period == 4:
            ordered_items= last_30_days_sales(item_cat)
            report_period = "Last 30 Days"
        elif report_period == 5:
            ordered_items = this_month_sales(item_cat)
            report_period = "This Month"
        elif report_period == 6:
            ordered_items = last_month_sales(item_cat)
            report_period = "Last Month"
        
           
    for ordered_items_count in ordered_items:
        if ordered_items_count.sum !=None and ordered_items_count.total !=None and ordered_items_count.vat_value:
            total_items_ordered += int(ordered_items_count.sum)
            total_vat += Money(ordered_items_count.vat_value, 'MWK')
            total_cost_items_ordered += Money(ordered_items_count.total, 'MWK')

    total_vat_iclusive = total_cost_items_ordered + total_vat

    context = {
        "item_cat":item_cat,
        "report_period":report_period,
        "item_categories":item_categories,
        "default_report_form":default_report_form,
        "form":form,
        "ordered_items":ordered_items,
        "total_items_ordered":total_items_ordered,
        "total_cost_items_ordered":total_cost_items_ordered,
        "total_vat":total_vat,
        "total_vat_iclusive":total_vat_iclusive,
        "config":config,
    }
    # return render(request, 'reports_dashboard.html',context)
    return render(request, 'sales_report.html',context)

def allds(x):
    ald = all_days_sales(x)
    return ald
def tod(x):
    todaysales = today_sales(x)
    return todaysales
def ytd (x):
    yts = yesterday_sales(x)
    return yts
def ls7dy(x):
    ls7 = last_7_days_sales(x)
    return ls7
def ls30dy(x):
    l30d = last_30_days_sales(x)
    return l30d
def thmon(x):
    thm = this_month_sales(x)
    return thm
def lmonth(x):
    lmo = last_month_sales(x)
    return lmo

def summery_of_sales(request):
    item_cats = ItemCategory.objects.all()
    #all days sales
    
    
    today_start_day = datetime.now().date()

    #all time sales summery
    palldays = get_summery_sales_all_days(today_start_day)
    grand_all_days = palldays.aggregate(grand_quantity = Sum('total_quantity'))
    grand_total_all_days = palldays.aggregate(grand_total = Sum('sales_total'))

    #todays sales summery
    ptoday = get_summery_sales(today_start_day, today_start_day )
    grand_today = ptoday.aggregate(grand_quantity = Sum('total_quantity'))
    grand_total = ptoday.aggregate(grand_total = Sum('sales_total'))

    #yesterday sales summery
    yesterday_start_day = datetime.now().date() - timedelta(days=1)
    pyesterday = get_summery_sales(yesterday_start_day, yesterday_start_day)
    grand_yesterday = pyesterday.aggregate(grand_quantity = Sum('total_quantity'))
    grand_total_yesterday = pyesterday.aggregate(grand_total = Sum('sales_total'))

    #last 7 days sales summery
    last7days_start_day = datetime.now().date() - timedelta(days=8)
    last7days_end_day = datetime.now().date() - timedelta(days=1)
    plast7days = get_summery_sales(last7days_start_day, last7days_end_day)
    grand_last7days = plast7days.aggregate(grand_quantity = Sum('total_quantity'))
    grand_total_last7days = plast7days.aggregate(grand_total = Sum('sales_total'))

    #last 30 days sales summery
    last30days_start_day = datetime.now().date() - timedelta(days=31)
    last30days_end_day = datetime.now().date() - timedelta(days=1)
    plast30days = get_summery_sales(last30days_start_day, last30days_end_day)
    grand_last30days = plast30days.aggregate(grand_quantity = Sum('total_quantity'))
    grand_total_last30days = plast30days.aggregate(grand_total = Sum('sales_total'))
   
    context = {
        "item_cats":item_cats,

        "palldays":palldays,
        "grand_all_days":grand_all_days,
        "grand_total_all_days":grand_total_all_days,

        "ptoday":ptoday,
        "grand_today":grand_today, 
        "grand_total":grand_total,

        "pyesterday":pyesterday,
        "grand_yesterday":grand_yesterday, 
        "grand_total_yesterday":grand_total_yesterday,

        "plast7days":plast7days,
        "grand_last7days":grand_last7days, 
        "grand_total_last7days":grand_total_last7days,

        "plast30days":plast30days,
        "grand_last30days":grand_last30days, 
        "grand_total_last30days":grand_total_last30days,
        
    }
    return render(request, 'summery_of_sales.html', context)

def get_summery_sales_all_days(todays_date):
    todays_date = todays_date
    return Item.objects.filter(orderitem__ordered_time__lte = todays_date).values('category__category_name').annotate(total_quantity=Sum('orderitem__quantity')).annotate(sales_total = Sum('orderitem__ordered_items_total', output_field = FloatField()))


def get_summery_sales(start_date, end_date):
    start_d = start_date
    end_d = end_date
    start_date_time = datetime.combine(start_d, time(00, 0))
    print(start_date_time)
    end_date_time = datetime.combine(end_d, time(23, 0)) + timedelta(minutes=59) + timedelta(seconds=59)
    print(end_date_time)
    print(end_date_time - start_date_time)
    sales = Item.objects.filter(orderitem__ordered_time__range = [start_date_time, end_date_time]).values('category__category_name').annotate(total_quantity=Sum('orderitem__quantity')).annotate(sales_total = Sum('orderitem__ordered_items_total', output_field = FloatField() ))
    print(sales)
    return sales

def get_item_names_in_orders():
    ordered_items = OrderItem.objects.order_by().values('item__item_name').filter(ordered = True).distinct()
    return ordered_items

def all_days_sales(category):
    now = timezone.now()
    #print(now)
    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)
    #print(get_item_cat)
    if get_item_cat.exists():
        vat = vat_rate()
        return Item.objects.filter(category__category_name = category_id).filter(orderitem__ordered_time__lte = now).annotate(sum=Sum('orderitem__quantity')).annotate(total = Sum(F('orderitem__quantity')*F('orderitem__item__price'), output_field = FloatField())).annotate(default_item_price = Sum(F('price')*1)).annotate(item_price = Sum(F('orderitem__item__price')*1)).annotate(vat_value = Sum(F('orderitem__quantity')*F('orderitem__item__price')*vat, output_field = FloatField())).annotate(tota_vat_inclusive = Sum((F('orderitem__quantity')*F('orderitem__item__price')*vat) + (F('orderitem__quantity')*F('orderitem__item__price')), output_field = FloatField()))   
    else:
        vat = vat_rate()
        return Item.objects.filter(orderitem__ordered_time__lte = now).annotate(sum=Sum('orderitem__quantity')).annotate(total = Sum(F('orderitem__quantity')*F('orderitem__item__price'), output_field = FloatField())).annotate(default_item_price = Sum(F('price')*1)).annotate(item_price = Sum(F('orderitem__item__price')*1)).annotate(vat_value = Sum(F('orderitem__quantity')*F('orderitem__item__price')*vat, output_field = FloatField())).annotate(tota_vat_inclusive = Sum((F('orderitem__quantity')*F('orderitem__item__price')*vat) + (F('orderitem__quantity')*F('orderitem__item__price')), output_field = FloatField()))   

def today_sales(category):
    yesterday = timezone.now().date()-timedelta(days=1)
    #print(yesterday)
    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)
    #print(get_item_cat)
    if get_item_cat.exists():
        vat = vat_rate()
        return Item.objects.filter(category__category_name = category_id).filter(orderitem__ordered_time__gt = yesterday).annotate(sum=Sum('orderitem__quantity')).annotate(total = Sum(F('orderitem__quantity')*F('orderitem__item__price'), output_field = FloatField())).annotate(default_item_price = Sum(F('price')*1)).annotate(item_price = Sum(F('orderitem__item__price')*1)).annotate(vat_value = Sum(F('orderitem__quantity')*F('orderitem__item__price')*vat, output_field = FloatField())).annotate(tota_vat_inclusive = Sum((F('orderitem__quantity')*F('orderitem__item__price')*vat) + (F('orderitem__quantity')*F('orderitem__item__price')), output_field = FloatField()))   
    else:
        vat = vat_rate()
        return Item.objects.filter(orderitem__ordered_time__gt = yesterday).annotate(sum=Sum('orderitem__quantity')).annotate(total = Sum(F('orderitem__quantity')*F('orderitem__item__price'), output_field = FloatField())).annotate(default_item_price = Sum(F('price')*1)).annotate(item_price = Sum(F('orderitem__item__price')*1)).annotate(vat_value = Sum(F('orderitem__quantity')*F('orderitem__item__price')*vat, output_field = FloatField())).annotate(tota_vat_inclusive = Sum((F('orderitem__quantity')*F('orderitem__item__price')*vat) + (F('orderitem__quantity')*F('orderitem__item__price')), output_field = FloatField()))   
        
def yesterday_sales(category):
    
    today = timezone.now().date()
    yesterday = today -timedelta(days=1)
    # print(yesterday)
    # print(today)
    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)
    #print(get_item_cat)
    if get_item_cat.exists():
        vat = vat_rate()
        return Item.objects.filter(category__category_name = category_id).filter(orderitem__ordered_time__range = [yesterday, today]).annotate(sum=Sum('orderitem__quantity')).annotate(total = Sum(F('orderitem__quantity')*F('orderitem__item__price'), output_field = FloatField())).annotate(default_item_price = Sum(F('price')*1)).annotate(item_price = Sum(F('orderitem__item__price')*1)).annotate(vat_value = Sum(F('orderitem__quantity')*F('orderitem__item__price')*vat, output_field = FloatField())).annotate(tota_vat_inclusive = Sum((F('orderitem__quantity')*F('orderitem__item__price')*vat) + (F('orderitem__quantity')*F('orderitem__item__price')), output_field = FloatField()))   
    else:
        vat = vat_rate()
        return Item.objects.filter(orderitem__ordered_time__range = [yesterday, today]).annotate(sum=Sum('orderitem__quantity')).annotate(total = Sum(F('orderitem__quantity')*F('orderitem__item__price'), output_field = FloatField())).annotate(default_item_price = Sum(F('price')*1)).annotate(item_price = Sum(F('orderitem__item__price')*1)).annotate(vat_value = Sum(F('orderitem__quantity')*F('orderitem__item__price')*vat, output_field = FloatField())).annotate(tota_vat_inclusive = Sum((F('orderitem__quantity')*F('orderitem__item__price')*vat) + (F('orderitem__quantity')*F('orderitem__item__price')), output_field = FloatField()))   
def last_7_days_sales(category):
    date_today = datetime.now().date()
    seven_days_b4 = date_today-timedelta(days=7)
    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)
    # print(date_today)
    # print(seven_days_b4)
    if get_item_cat.exists():
        vat = vat_rate()
        return Item.objects.filter(category__category_name = category_id).filter(orderitem__ordered_time__range = [seven_days_b4, date_today]).annotate(sum=Sum('orderitem__quantity')).annotate(total = Sum(F('orderitem__quantity')*F('orderitem__item__price'), output_field = FloatField())).annotate(default_item_price = Sum(F('price')*1)).annotate(item_price = Sum(F('orderitem__item__price')*1)).annotate(vat_value = Sum(F('orderitem__quantity')*F('orderitem__item__price')*vat, output_field = FloatField())).annotate(tota_vat_inclusive = Sum((F('orderitem__quantity')*F('orderitem__item__price')*vat) + (F('orderitem__quantity')*F('orderitem__item__price')), output_field = FloatField()))   
    else:
        vat = vat_rate()
        return Item.objects.filter(orderitem__ordered_time__range = [seven_days_b4, date_today]).annotate(sum=Sum('orderitem__quantity')).annotate(total = Sum(F('orderitem__quantity')*F('orderitem__item__price'), output_field = FloatField())).annotate(default_item_price = Sum(F('price')*1)).annotate(item_price = Sum(F('orderitem__item__price')*1)).annotate(vat_value = Sum(F('orderitem__quantity')*F('orderitem__item__price')*vat, output_field = FloatField())).annotate(tota_vat_inclusive = Sum((F('orderitem__quantity')*F('orderitem__item__price')*vat) + (F('orderitem__quantity')*F('orderitem__item__price')), output_field = FloatField()))   
def last_30_days_sales(category):
    date_today = datetime.now().date()
    thirty_days_b4 = date_today-timedelta(days=30)
    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)
    #print(date_today)
    #print(thirty_days_b4)
    if get_item_cat.exists():
        vat = vat_rate()
        return Item.objects.filter(category__category_name = category_id).filter(orderitem__ordered_time__range = [thirty_days_b4, date_today]).annotate(sum=Sum('orderitem__quantity')).annotate(total = Sum(F('orderitem__quantity')*F('orderitem__item__price'), output_field = FloatField())).annotate(default_item_price = Sum(F('price')*1)).annotate(item_price = Sum(F('orderitem__item__price')*1)).annotate(vat_value = Sum(F('orderitem__quantity')*F('orderitem__item__price')*vat, output_field = FloatField())).annotate(tota_vat_inclusive = Sum((F('orderitem__quantity')*F('orderitem__item__price')*vat) + (F('orderitem__quantity')*F('orderitem__item__price')), output_field = FloatField()))   
    else:
        vat = vat_rate()
        return Item.objects.filter(orderitem__ordered_time__range = [thirty_days_b4, date_today]).annotate(sum=Sum('orderitem__quantity')).annotate(total = Sum(F('orderitem__quantity')*F('orderitem__item__price'), output_field = FloatField())).annotate(default_item_price = Sum(F('price')*1)).annotate(item_price = Sum(F('orderitem__item__price')*1)).annotate(vat_value = Sum(F('orderitem__quantity')*F('orderitem__item__price')*vat, output_field = FloatField())).annotate(tota_vat_inclusive = Sum((F('orderitem__quantity')*F('orderitem__item__price')*vat) + (F('orderitem__quantity')*F('orderitem__item__price')), output_field = FloatField()))   
def this_month_sales(category):
    today = datetime.now()
    this_month_firstday = datetime.now().date().replace(day=1)
    
    #print(today)
    #print(this_month_firstday)
    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)
    if get_item_cat.exists():
        vat = vat_rate()
        return Item.objects.filter(category__category_name = category_id).filter(orderitem__ordered_time__range = [this_month_firstday, today]).annotate(sum=Sum('orderitem__quantity')).annotate(total = Sum(F('orderitem__quantity')*F('orderitem__item__price'), output_field = FloatField())).annotate(default_item_price = Sum(F('price')*1)).annotate(item_price = Sum(F('orderitem__item__price')*1)).annotate(vat_value = Sum(F('orderitem__quantity')*F('orderitem__item__price')*vat, output_field = FloatField())).annotate(tota_vat_inclusive = Sum((F('orderitem__quantity')*F('orderitem__item__price')*vat) + (F('orderitem__quantity')*F('orderitem__item__price')), output_field = FloatField()))   
    else:
        vat = vat_rate()
        return Item.objects.filter(orderitem__ordered_time__range = [this_month_firstday, today]).annotate(sum=Sum('orderitem__quantity')).annotate(total = Sum(F('orderitem__quantity')*F('orderitem__item__price'), output_field = FloatField())).annotate(default_item_price = Sum(F('price')*1)).annotate(item_price = Sum(F('orderitem__item__price')*1)).annotate(vat_value = Sum(F('orderitem__quantity')*F('orderitem__item__price')*vat, output_field = FloatField())).annotate(tota_vat_inclusive = Sum((F('orderitem__quantity')*F('orderitem__item__price')*vat) + (F('orderitem__quantity')*F('orderitem__item__price')), output_field = FloatField()))   
def last_month_sales(category):
    today = datetime.now().date()
    this_month_firstday = today.replace(day=1)
    last_monthlastday = this_month_firstday - timedelta(days=1)
    last_monthlastday2 = last_monthlastday
    last_monthfirstday = last_monthlastday2.replace(day=1)
    #print(last_monthfirstday)
    #print(last_monthlastday)
    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)
    if get_item_cat.exists():
        vat = vat_rate()
        return Item.objects.filter(category__category_name = category_id).filter(orderitem__ordered_time__range = [last_monthfirstday, last_monthlastday]).annotate(sum=Sum('orderitem__quantity')).annotate(total = Sum(F('orderitem__quantity')*F('orderitem__item__price'), output_field = FloatField())).annotate(default_item_price = Sum(F('price')*1)).annotate(item_price = Sum(F('orderitem__item__price')*1)).annotate(vat_value = Sum(F('orderitem__quantity')*F('orderitem__item__price')*vat, output_field = FloatField())).annotate(tota_vat_inclusive = Sum((F('orderitem__quantity')*F('orderitem__item__price')*vat) + (F('orderitem__quantity')*F('orderitem__item__price')), output_field = FloatField()))   
    else:
        vat = vat_rate()
        return Item.objects.filter(orderitem__ordered_time__range = [last_monthfirstday, last_monthlastday]).annotate(sum=Sum('orderitem__quantity')).annotate(total = Sum(F('orderitem__quantity')*F('orderitem__item__price'), output_field = FloatField())).annotate(default_item_price = Sum(F('price')*1)).annotate(item_price = Sum(F('orderitem__item__price')*1)).annotate(vat_value = Sum(F('orderitem__quantity')*F('orderitem__item__price')*vat, output_field = FloatField())).annotate(tota_vat_inclusive = Sum((F('orderitem__quantity')*F('orderitem__item__price')*vat) + (F('orderitem__quantity')*F('orderitem__item__price')), output_field = FloatField()))   

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

