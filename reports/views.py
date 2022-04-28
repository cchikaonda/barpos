from django.db.models.functions.datetime import TruncWeek
from django.shortcuts import render,redirect, get_object_or_404
from rest_framework.serializers import Serializer
from inventory.models import ItemCategory, Unit, Item, Stock
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
from inventory import views as inventory_views

@login_required
def reports_dashboard(request):
    items = Item.objects.all()
    sales_all_time = Order.objects.filter(ordered = True)

    
    total_cog = 0
    stocks = Stock.objects.all()
    
    for stock in stocks:
       total_cog += stock.get_total_cost_of_items

    
    ordered_items = OrderItem.objects.filter(ordered = True)
    sales_overtime = 0
    sales_tax = 0

    for sales_all_time in sales_all_time:
        sales_overtime += sales_all_time.total_paid_amount()
        sales_tax += sales_all_time.vat_cost
    
    orders_r = Order.objects.filter(ordered = False)
    lay_by_orders = LayByOrders.objects.filter(order_id__in = orders_r)
    lay_b_payments = Payment.objects.filter(laybyorders__in = lay_by_orders)
    sum_layby_paid_amount = Money(0.0, 'MWK')
    for lay_b_payments in lay_b_payments:
        if str(lay_b_payments.paid_amount) != "None":
            sum_layby_paid_amount += lay_b_payments.paid_amount
    
    sales_overtime += sum_layby_paid_amount
    
    monday_total_sales = inventory_views.get_total_sales_this_week(2)
    tuesday_total_sales = inventory_views.get_total_sales_this_week(3)
    wednesday_total_sales = inventory_views.get_total_sales_this_week(4)
    thursday_total_sales = inventory_views.get_total_sales_this_week(5)
    friday_total_sales = inventory_views.get_total_sales_this_week(6)
    saturday_total_sales = inventory_views.get_total_sales_this_week(7)
    sunday_total_sales = inventory_views.get_total_sales_this_week(1)


    lw_monday_total_sales = inventory_views.get_total_lastwk_sale(2)
    lw_tuesday_total_sales = inventory_views.get_total_lastwk_sale(3)
    lw_wednesday_total_sales = inventory_views.get_total_lastwk_sale(4)
    lw_thursday_total_sales = inventory_views.get_total_lastwk_sale(5)
    lw_friday_total_sales = inventory_views.get_total_lastwk_sale(6)
    lw_saturday_total_sales = inventory_views.get_total_lastwk_sale(7)
    lw_sunday_total_sales = inventory_views.get_total_lastwk_sale(1)

 
    form = SearchBetweenTwoDatesForm()
    default_report_form = DefaultReportsForm()
    ordered_items = OrderItem.objects.filter(ordered = True)
    item_categories = ItemCategory.objects.all().order_by('category_name')

    # total_sales = get_total_sales_for_each_day(all_ordered_items)
    total_paid_amount = get_todays_total_sales()
  
   
    todays_total_sales = get_todays_total_sales()
    yesterday_total_sales = get_yesterday_total_sales()
    
    

    today = timezone.now().date()

    ordered_items = yesterday_ordered_items(ordered_items)
    yesterdays_sales = Money(0.0, 'MWK') 
    for ordered_items_count in ordered_items:
        yesterdays_sales += ordered_items_count.ordered_items_total


    if request.method == "POST":
            from_date = request.POST.get('start_date_time')
            to_date = request.POST.get('end_date_time')

            report_period = request.POST.get('report_period')
            
            if report_period != None:
                repo_period = get_report_period(report_period)
                if repo_period == 1:
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
            'todays_total_sales':todays_total_sales,
            'yesterday_total_sales':yesterday_total_sales,
            'config':config,
            # 'total_sales':total_sales,
            'total_paid_amount':total_paid_amount,


            'lw_monday_total_sales':lw_monday_total_sales,
            'lw_tuesday_total_sales':lw_tuesday_total_sales,
            'lw_wednesday_total_sales':lw_wednesday_total_sales,
            'lw_thursday_total_sales':lw_thursday_total_sales,
            'lw_friday_total_sales':lw_friday_total_sales,
            'lw_saturday_total_sales':lw_saturday_total_sales,
            'lw_sunday_total_sales':lw_sunday_total_sales,

            'monday_total_sales':monday_total_sales,
            'tuesday_total_sales':tuesday_total_sales,
            'wednesday_total_sales':wednesday_total_sales,
            'thursday_total_sales':thursday_total_sales,
            'friday_total_sales':friday_total_sales,
            'saturday_total_sales':saturday_total_sales,
            'sunday_total_sales':sunday_total_sales,
            'sales_overtime':sales_overtime,
            'sales_tax':sales_tax,
            'items':items,
            'total_cog':total_cog,


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
        'todays_total_sales':todays_total_sales,
        'yesterday_total_sales':yesterday_total_sales,
        'config':config,
        # 'total_sales':total_sales,
        'total_paid_amount':total_paid_amount,

        'lw_monday_total_sales':lw_monday_total_sales,
        'lw_tuesday_total_sales':lw_tuesday_total_sales,
        'lw_wednesday_total_sales':lw_wednesday_total_sales,
        'lw_thursday_total_sales':lw_thursday_total_sales,
        'lw_friday_total_sales':lw_friday_total_sales,
        'lw_saturday_total_sales':lw_saturday_total_sales,
        'lw_sunday_total_sales':lw_sunday_total_sales,

        'monday_total_sales':monday_total_sales,
        'tuesday_total_sales':tuesday_total_sales,
        'wednesday_total_sales':wednesday_total_sales,
        'thursday_total_sales':thursday_total_sales,
        'friday_total_sales':friday_total_sales,
        'saturday_total_sales':saturday_total_sales,
        'sunday_total_sales':sunday_total_sales,
        'sales_overtime':sales_overtime,
        'sales_tax':sales_tax,
        'items':items,
        'total_cog':total_cog,
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

# def get_todays_total_sales():
#     today_date = timezone.now().date()
#     todays_sales = Order.objects.filter(ordered=True).filter(order_date__gte=today_date)
#     todays_ordered_items = OrderItem.objects.filter(ordered = True).filter(ordered_time__gte = today_date).order_by('ordered_time')
#     return todays_ordered_items

def get_todays_total_sales():
    today_date = timezone.now().date()
    total_sales = Payment.objects.filter(created_at__gte=today_date)
    sum_total_cost = 0
    for total_sales in total_sales:
        sum_total_cost += total_sales.paid_amount
    return sum_total_cost 
 

def get_yesterday_total_sales():
    today_date = timezone.now().date()
    yesterday_date = today_date - timedelta(days=1)
    total_sales = Payment.objects.filter(created_at__range = [yesterday_date, today_date])

    sum_total_cost = 0
    for total_sales in total_sales:
        sum_total_cost += total_sales.paid_amount
    return sum_total_cost 


def get_all_item_categories():
    return ItemCategory.objects.all().order_by('category_name')

def get_total_sales_for_each_day(todays_ordered_items):
    total_sales = 0
    for todays_ordered_item in todays_ordered_items:
        total_sales += todays_ordered_item.ordered_items_total
    return total_sales

def get_total_amount_paid():
    orders = Order.objects.all()
    total_paid = 0
    for order in orders:
        total_paid += order.paid_amount.paid_amount
    return total_paid

def get_total_quantity_for_each_day(todays_ordered_items):
    total_quantity = 0
    for todays_ordered_item in todays_ordered_items:
        total_quantity += todays_ordered_item.quantity
    return total_quantity

@login_required
def sales_report(request):
    item_cat = "All Categories"
    report_period = "All Days"

    total_items_ordered = 0
    total_cost_items_ordered = Money('0.0', 'MWK')

    item_categories = ItemCategory.objects.all().order_by('category_name')

    ordered_items = all_days_sales(report_period)

    today = timezone.now().date()
    report_time = timezone.now()
    yesterday = today-timedelta(days=1)
    
    if request.method == "POST":
        item_cat = request.POST.get('item_categories_option')
        report_period = request.POST.get('report_period')
        report_period = int(report_period)
        if report_period == 777:
            ordered_items = all_days_sales(item_cat)
            report_period = "All Days"
            orders_r = Order.objects.filter(ordered = False)
            lay_by_orders = LayByOrders.objects.filter(order_id__in = orders_r)
            lay_b_payments = Payment.objects.filter(laybyorders__in = lay_by_orders)
            sum_layby_paid_amount = Money(0.0, 'MWK')
            for lay_b_payments in lay_b_payments:
                if str(lay_b_payments.paid_amount) != "None":
                    sum_layby_paid_amount += lay_b_payments.paid_amount
        elif report_period == 1:
            ordered_items = todays_ordered_items(item_cat)
            report_period = "Today"

            orders_r = Order.objects.all()
            today_payments = Payment.objects.filter(order__id__in = orders_r, created_at__gte = today)
            sum_today_payments = Money(0.0, 'MWK')
            for today_payment in today_payments:
                if str(today_payment.paid_amount) != "None":
                    sum_today_payments += today_payment.paid_amount
            

            orders_r = Order.objects.filter(order_type = 'Lay By', ordered = False)
            today_layby_payments = Payment.objects.filter(order__id__in = orders_r, order_type = 'Lay By', created_at__gte = today)
            
            sum_layby_paid_amount = Money(0.0, 'MWK')
            for today_layby_payments in today_layby_payments:
                if str(today_layby_payments.paid_amount) != "None":
                    sum_layby_paid_amount += today_layby_payments.paid_amount
            
         
        elif report_period == 2:
            ordered_items = yesterday_ordered_items(item_cat)
            report_period = "Yesterday"
            date_today = datetime.now().date()

            orders_r = Order.objects.filter(ordered = False)
            lay_by_orders = LayByOrders.objects.filter(order_id__in = orders_r)
            lay_b_payments = Payment.objects.filter(laybyorders__in = lay_by_orders, created_at__gte = yesterday,created_at__lt = date_today)
            sum_layby_paid_amount = Money(0.0, 'MWK')
            for lay_b_payments in lay_b_payments:
                if str(lay_b_payments.paid_amount) != "None":
                    sum_layby_paid_amount += lay_b_payments.paid_amount
  
        elif report_period == 3:
            ordered_items = last_7_days_ordered_items(item_cat)
            report_period = "Last 7 Days"

            date_today = datetime.now().date()
            seven_days_b4 = date_today-timedelta(days=7)

            orders_r = Order.objects.filter(ordered = False)
            lay_by_orders = LayByOrders.objects.filter(order_id__in = orders_r)
            lay_b_payments = Payment.objects.filter(laybyorders__in = lay_by_orders, created_at__range = [seven_days_b4, date_today])
            sum_layby_paid_amount = Money(0.0, 'MWK')
            for lay_b_payments in lay_b_payments:
                if str(lay_b_payments.paid_amount) != "None":
                    sum_layby_paid_amount += lay_b_payments.paid_amount
            
        elif report_period == 4:
            ordered_items= last_30_days_ordered_items(item_cat)
            report_period = "Last 30 Days"

            date_today = datetime.now().date()
            thirty_days_b4 = date_today-timedelta(days=30)

            orders_r = Order.objects.filter(ordered = False)
            lay_by_orders = LayByOrders.objects.filter(order_id__in = orders_r)
            lay_b_payments = Payment.objects.filter(laybyorders__in = lay_by_orders, created_at__range = [thirty_days_b4, date_today])
            sum_layby_paid_amount = Money(0.0, 'MWK')
            for lay_b_payments in lay_b_payments:
                if str(lay_b_payments.paid_amount) != "None":
                    sum_layby_paid_amount += lay_b_payments.paid_amount

        elif report_period == 5:
            ordered_items = this_month_ordered_items(item_cat)
            report_period = "This Month"
            
            today = datetime.now()
            this_month_firstday = datetime.now().date().replace(day=1)

            orders_r = Order.objects.filter(ordered = False)
            lay_by_orders = LayByOrders.objects.filter(order_id__in = orders_r)
            lay_b_payments = Payment.objects.filter(laybyorders__in = lay_by_orders, created_at__range = [this_month_firstday, today])
            sum_layby_paid_amount = Money(0.0, 'MWK')
            for lay_b_payments in lay_b_payments:
                if str(lay_b_payments.paid_amount) != "None":
                    sum_layby_paid_amount += lay_b_payments.paid_amount

        elif report_period == 6:
            ordered_items = last_month_ordered_items(item_cat)
            report_period = "Last Month"

            today = datetime.now().date()
            this_month_firstday = today.replace(day=1)
            last_monthlastday = this_month_firstday - timedelta(days=1)
            last_monthlastday2 = last_monthlastday
            last_monthfirstday = last_monthlastday2.replace(day=1)

            orders_r = Order.objects.filter(ordered = False)
            lay_by_orders = LayByOrders.objects.filter(order_id__in = orders_r)
            lay_b_payments = Payment.objects.filter(laybyorders__in = lay_by_orders, created_at__range = [last_monthfirstday, last_monthlastday])
            sum_layby_paid_amount = Money(0.0, 'MWK')
            for lay_b_payments in lay_b_payments:
                if str(lay_b_payments.paid_amount) != "None":
                    sum_layby_paid_amount += lay_b_payments.paid_amount 
    else:
        orders_r = Order.objects.filter(ordered = False)
        lay_by_orders = LayByOrders.objects.filter(order_id__in = orders_r)
        lay_b_payments = Payment.objects.filter(laybyorders__in = lay_by_orders)
        sum_layby_paid_amount = Money(0.0, 'MWK')
        for lay_b_payments in lay_b_payments:
            if str(lay_b_payments.paid_amount) != "None":
                sum_layby_paid_amount += lay_b_payments.paid_amount

        
    sum_total_vat = Money(0.0, 'MWK')
    # orders_with_ordered_items = Order.objects.all()
    orders_with_ordered_items = Order.objects.filter(items__in = ordered_items)
    for order in orders_with_ordered_items:
        sum_total_vat += order.vat_cost
    
    sum_ordered_items_count = 0
    total_cost_items_ordered = Money(0.0, 'MWK') 
    for ordered_items_count in ordered_items:
        sum_ordered_items_count += ordered_items_count.quantity
        total_cost_items_ordered += ordered_items_count.ordered_items_total

    net_total_sales = total_cost_items_ordered -sum_total_vat

    
    total_cash_in_hand = sum_layby_paid_amount + total_cost_items_ordered
    other_payments = total_cash_in_hand - sum_layby_paid_amount - total_cost_items_ordered

    context = {
        "item_cat":item_cat,
        "report_period":report_period,
        "item_categories":item_categories,
        "ordered_items":ordered_items,
        "total_items_ordered":total_items_ordered,
        "total_cost_items_ordered":total_cost_items_ordered,
        "config":config,
        "sum_ordered_items_count":sum_ordered_items_count,
        "sum_total_vat":sum_total_vat,
        "net_total_sales":net_total_sales,
        # "sum_today_payments":sum_today_payments,
        "total_cash_in_hand":total_cash_in_hand,
        "report_time":report_time,
        "sum_layby_paid_amount":sum_layby_paid_amount,
        "other_payments":other_payments,
    }
    return render(request, 'sales_report.html',context)

@login_required
def sales_report_custom_range(request):
    form = SearchBetweenTwoDatesForm()
    item_cat = "All Categories"
    
    total_items_ordered = 0
    total_cost_items_ordered = Money('0.0', 'MWK')

    item_categories = ItemCategory.objects.all().order_by('category_name')

    ordered_items = all_days_sales(0)

    if request.method == "POST":
        if form.is_valid:
            from_date = request.POST.get('start_date_time')
            to_date = request.POST.get('end_date_time')
        
            item_cat = request.POST.get('item_categories_option')

        
        if is_valid_queryparam(from_date) and is_valid_queryparam(to_date):
            category_id = item_cat
            get_item_cat = ItemCategory.objects.filter(category_name = category_id)
            if get_item_cat.exists():
                ordered_items = ordered_items.filter(ordered_time__gte = from_date, ordered_time__lte = to_date, item__category__in = get_item_cat)
            ordered_items = ordered_items.filter(ordered_time__gte = from_date, ordered_time__lte = to_date)
        orders_r = Order.objects.filter(ordered = False)

        lay_by_orders = LayByOrders.objects.filter(order_id__in = orders_r)
        lay_b_payments = Payment.objects.filter(laybyorders__in = lay_by_orders, created_at__gte = from_date, created_at__lte = to_date)
        sum_layby_paid_amount = Money(0.0, 'MWK')
        for lay_b_payments in lay_b_payments:
            if str(lay_b_payments.paid_amount) != "None":
                sum_layby_paid_amount += lay_b_payments.paid_amount
    else:
        orders_r = Order.objects.filter(ordered = False)
        lay_by_orders = LayByOrders.objects.filter(order_id__in = orders_r)
        lay_b_payments = Payment.objects.filter(laybyorders__in = lay_by_orders)
        sum_layby_paid_amount = Money(0.0, 'MWK')
        for lay_b_payments in lay_b_payments:
            if str(lay_b_payments.paid_amount) != "None":
                sum_layby_paid_amount += lay_b_payments.paid_amount

    sum_total_vat = Money(0.0, 'MWK')
    # orders_with_ordered_items = Order.objects.all()
    orders_with_ordered_items = Order.objects.filter(ordered = True, items__in = ordered_items)
    for order in orders_with_ordered_items:
        sum_total_vat += order.vat_cost
    
    sum_ordered_items_count = 0
    total_cost_items_ordered = Money(0.0, 'MWK') 
    for ordered_items_count in ordered_items:
        sum_ordered_items_count += ordered_items_count.quantity
        total_cost_items_ordered += ordered_items_count.ordered_items_total

    net_total_sales =  total_cost_items_ordered - sum_total_vat
    total_cash_in_hand = total_cost_items_ordered + sum_layby_paid_amount

    context = {
        "item_cat":item_cat,
        "item_categories":item_categories,
        "form":form,
        "ordered_items":ordered_items,
        "total_items_ordered":total_items_ordered,
        "total_cost_items_ordered":total_cost_items_ordered,
        "config":config,
        "sum_ordered_items_count":sum_ordered_items_count,
        "sum_total_vat":sum_total_vat,
        "net_total_sales":net_total_sales,
        "sum_layby_paid_amount":sum_layby_paid_amount,
        "total_cash_in_hand":total_cash_in_hand,
    }
    return render(request, 'sales_report_custom_range.html',context)

def allds(x):
    ald = all_days_sales(x)
    return ald
def tod(x):
    todaysales = todays_ordered_items(x)
    return todaysales
def ytd (x):
    yts = yesterday_ordered_items(x)
    return yts
def ls7dy(x):
    ls7 = last_7_days_ordered_items(x)
    return ls7
def ls30dy(x):
    l30d = last_30_days_ordered_items(x)
    return l30d
def thmon(x):
    thm = this_month_ordered_items(x)
    return thm
def lmonth(x):
    lmo = last_month_ordered_items(x)
    return lmo

@login_required
def summery_of_sales(request):
    item_cats = ItemCategory.objects.all()
    #all days sales
    
    
    today_start_day = datetime.now()

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
    last7days_start_day = datetime.now().date() - timedelta(days=7)
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

    #this month sales summery
    today = datetime.now()
    this_month_firstday = datetime.now().date().replace(day=1)
    thismonthsales = get_summery_sales(this_month_firstday, today)
    grand_thismonth = thismonthsales.aggregate(grand_quantity = Sum('total_quantity'))
    grand_total_thismonth = thismonthsales.aggregate(grand_total = Sum('sales_total'))
    
    #last month sales
    today = datetime.now().date()
    this_month_firstday = today.replace(day=1)
    last_monthlastday = this_month_firstday - timedelta(days=1)
    last_monthlastday2 = last_monthlastday
    last_monthfirstday = last_monthlastday2.replace(day=1)
    lastmonthsales = get_summery_sales(last_monthfirstday, last_monthlastday)
    grand_lastmonth = lastmonthsales.aggregate(grand_quantity = Sum('total_quantity'))
    grand_total_lastmonth = lastmonthsales.aggregate(grand_total = Sum('sales_total'))

    # this year sales
    this_year_sales = Item.objects.filter(orderitem__ordered_time__year = today.year).values('category__category_name').annotate(total_quantity=Sum('orderitem__quantity')).annotate(sales_total = Sum('orderitem__ordered_items_total', output_field = FloatField() ))
    grand_this_year = this_year_sales.aggregate(grand_quantity = Sum('total_quantity'))
    grand_total_this_year = this_year_sales.aggregate(grand_total = Sum('sales_total'))
   
    #last year sales
    last_year = today.year - 1
    last_year_sales = Item.objects.filter(orderitem__ordered_time__year = last_year).values('category__category_name').annotate(total_quantity=Sum('orderitem__quantity')).annotate(sales_total = Sum('orderitem__ordered_items_total', output_field = FloatField() ))
    grand_last_year = last_year_sales.aggregate(grand_quantity = Sum('total_quantity'))
    grand_total_last_year = last_year_sales.aggregate(grand_total = Sum('sales_total'))



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

        "thismonthsales":thismonthsales,
        "grand_thismonth":grand_thismonth,
        "grand_total_thismonth":grand_total_thismonth,
        "lastmonthsales":lastmonthsales,
        "grand_lastmonth":grand_lastmonth,
        "grand_total_lastmonth":grand_total_lastmonth,

        "this_year_sales":this_year_sales,
        "grand_this_year":grand_this_year,
        "grand_total_this_year":grand_total_this_year,
        
        "last_year_sales":last_year_sales,
        "grand_last_year":grand_last_year,
        "grand_total_last_year":grand_total_last_year,
    }
    return render(request, 'summery_of_sales.html', context)

def get_summery_sales_all_days(todays_date):
    todays_date = todays_date
    sales = Item.objects.filter(orderitem__ordered_time__lte = todays_date).values('category__category_name').annotate(total_quantity=Sum('orderitem__quantity')).annotate(sales_total = Sum('orderitem__ordered_items_total', output_field = FloatField() ))
    return sales
    

def get_summery_sales(start_date, end_date):
    start_d = start_date
    end_d = end_date
    start_date_time = datetime.combine(start_d, time(00, 0))
    end_date_time = datetime.combine(end_d, time(23, 0)) + timedelta(minutes=59) + timedelta(seconds=59)
    sales = Item.objects.filter(orderitem__ordered_time__range = [start_date_time, end_date_time]).values('category__category_name').annotate(total_quantity=Sum('orderitem__quantity')).annotate(sales_total = Sum('orderitem__ordered_items_total', output_field = FloatField() ))
    return sales

def get_item_names_in_orders():
    ordered_items = OrderItem.objects.order_by().values('item__item_name').all().distinct()
    return ordered_items

def all_days_sales(category):
    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)
    if get_item_cat.exists():
        return OrderItem.objects.filter(ordered = True, item__category__in = get_item_cat)
    else:
        return OrderItem.objects.filter(ordered = True)

def todays_ordered_items(category):
    today = timezone.now().date()
    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)
    if get_item_cat.exists():
        return OrderItem.objects.filter(ordered = True, item__category__in = get_item_cat, ordered_time__gte = today)  
    else:
        return OrderItem.objects.filter(ordered = True, ordered_time__gte = today)

def yesterday_ordered_items(category):
    today = timezone.now().date()
    yesterday = today -timedelta(days=1)
    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)
    if get_item_cat.exists():
        return OrderItem.objects.filter(ordered = True, item__category__in = get_item_cat, ordered_time__range = [yesterday, today])
    else:
        return OrderItem.objects.filter(ordered = True, ordered_time__range = [yesterday, today])

def last_7_days_ordered_items(category):
    date_today = datetime.now().date()
    seven_days_b4 = date_today-timedelta(days=7)

    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)

    if get_item_cat.exists():
        return OrderItem.objects.filter(ordered = True, item__category__in = get_item_cat, ordered_time__range = [seven_days_b4, date_today])
    else:
        return OrderItem.objects.filter(ordered = True, ordered_time__range = [seven_days_b4, date_today])
def last_30_days_ordered_items(category):
    date_today = datetime.now().date()
    thirty_days_b4 = date_today-timedelta(days=30)
    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)
    if get_item_cat.exists():
        return OrderItem.objects.filter(ordered = True, item__category__in = get_item_cat, ordered_time__range = [thirty_days_b4, date_today])
    else:
        return OrderItem.objects.filter(ordered = True, ordered_time__range = [thirty_days_b4, date_today])
def this_month_ordered_items(category):
    today = datetime.now()
    this_month_firstday = datetime.now().date().replace(day=1)
    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)
    if get_item_cat.exists():
        return OrderItem.objects.filter(ordered = True, item__category__in = get_item_cat, ordered_time__range = [this_month_firstday, today])
    else:
       return OrderItem.objects.filter(ordered = True, ordered_time__range = [this_month_firstday, today])
def last_month_ordered_items(category):
    today = datetime.now().date()
    this_month_firstday = today.replace(day=1)
    last_monthlastday = this_month_firstday - timedelta(days=1)
    last_monthlastday2 = last_monthlastday
    last_monthfirstday = last_monthlastday2.replace(day=1)
    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)
    if get_item_cat.exists():
        return OrderItem.objects.filter(ordered = True, item__category__in = get_item_cat, ordered_time__range = [last_monthfirstday, last_monthlastday])
        # return Item.objects.filter(category__category_name = category_id).filter(orderitem__ordered_time__range = [last_monthfirstday, last_monthlastday]).annotate(sum=Sum('orderitem__quantity')).annotate(total = Sum(F('orderitem__quantity')*F('orderitem__ordered_item_price'), output_field = FloatField())).annotate(default_item_price = Sum(F('price')*1)).annotate(item_price = Sum(F('orderitem__ordered_item_price')*1)).annotate(vat_value = Sum(F('orderitem__quantity')*F('orderitem__ordered_item_price')*vat, output_field = FloatField())).annotate(tota_vat_inclusive = Sum((F('orderitem__quantity')*F('orderitem__ordered_item_price')*vat) + (F('orderitem__quantity')*F('orderitem__ordered_item_price')), output_field = FloatField()))   
    else:
        return OrderItem.objects.filter(ordered = True,ordered_time__range = [last_monthfirstday, last_monthlastday])

def count_items_in_orders_by_item_using_range(from_date, to_date, category_id):
    from_d = from_date
    to_d = to_date
    vat = vat_rate()
    if category_id !=None:
        ordered_items_count = Item.objects.filter(category__id = category_id).filter(orderitem__ordered_time__range = [from_d, to_d]).annotate(sum=Sum('orderitem__quantity')).annotate(total = Sum(F('orderitem__quantity')*F('orderitem__ordered_item_price'), output_field = FloatField())).annotate(default_item_price = Sum(F('price')*1)).annotate(item_price = Sum(F('orderitem__ordered_item_price')*1)).annotate(vat_value = Sum(F('orderitem__quantity')*F('orderitem__ordered_item_price')*vat, output_field = FloatField())).annotate(tota_vat_inclusive = Sum((F('orderitem__quantity')*F('orderitem__ordered_item_price')*vat) + (F('orderitem__quantity')*F('orderitem__ordered_item_price')), output_field = FloatField()))
    ordered_items_count = Item.objects.filter(orderitem__ordered_time__range = [from_d, to_d]).annotate(sum=Sum('orderitem__quantity')).annotate(total = Sum(F('orderitem__quantity')*F('orderitem__ordered_item_price'), output_field = FloatField())).annotate(default_item_price = Sum(F('price')*1)).annotate(item_price = Sum(F('orderitem__ordered_item_price')*1)).annotate(vat_value = Sum(F('orderitem__quantity')*F('orderitem__ordered_item_price')*vat, output_field = FloatField())).annotate(tota_vat_inclusive = Sum((F('orderitem__quantity')*F('orderitem__ordered_item_price')*vat) + (F('orderitem__quantity')*F('orderitem__ordered_item_price')), output_field = FloatField()))
    return ordered_items_count

def vat_rate():
    return float(config.TAX_NAME)/100.00

def sales_report_data(request):
    items = OrderItem.objects.all()
    selialised_items = OrderItemSerializer(items, many=True)
    return JsonResponse(selialised_items.data,safe=False)

