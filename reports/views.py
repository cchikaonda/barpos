from enum import unique
from unicodedata import category
from django.db.models.functions.datetime import TruncWeek
from django.shortcuts import render,redirect, get_object_or_404
from rest_framework.serializers import Serializer
from expenses.models import Expense, ExpenseCategory
from inventory.models import ItemCategory, Unit, Item, Stock
from pos.models import Customer, OrderItem, Order, Payment, MoneyOutput
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
from django.db.models import AutoField,IntegerField,FloatField,ExpressionWrapper, F, DecimalField, Count, Sum, Max

from djmoney.models.managers import understands_money
from inventory import views as inventory_views

from django.db.models.functions import Greatest

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


def get_todays_total_sales():
    today_date = timezone.now().date()
    total_sales = Payment.objects.filter(updated_at__gte=today_date)
    sum_total_cost = 0
    for total_sales in total_sales:
        sum_total_cost += total_sales.paid_amount
    return sum_total_cost 
 

def get_yesterday_total_sales():
    today_date = timezone.now().date()
    yesterday_date = today_date - timedelta(days=1)
    total_sales = Payment.objects.filter(updated_at__range = [yesterday_date, today_date])

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

    payments = Payment.objects.all()
    
    sum_total_vat = Money(0.0, 'MWK')
    orders = Order.objects.filter(ordered = True)
    for order in orders:
        sum_total_vat += order.vat_cost

    if request.method == "POST":
        item_cat = request.POST.get('item_categories_option')
        report_period = request.POST.get('report_period')
        report_period = int(report_period)
        if report_period == 777:
            ordered_items = all_days_sales(item_cat)
            report_period = "All Days"
            orders_r = Order.objects.filter(ordered = False)
        elif report_period == 1:
            ordered_items = todays_ordered_items(item_cat)
            report_period = "Today"

            orders_r = Order.objects.all()
            today_payments = Payment.objects.filter(order__id__in = orders_r, updated_at__gte = today)
            
            payments = today_payments

            sum_total_vat = Money(0.0, 'MWK')
            orders = Order.objects.filter(ordered = True, updated_at__gte = today)
            for order in orders:
                sum_total_vat += order.vat_cost
            

            sum_today_payments = Money(0.0, 'MWK')
            for today_payment in today_payments:
                if str(today_payment.paid_amount) != "None":
                    sum_today_payments += today_payment.paid_amount
            

            orders_r = Order.objects.filter(order_type = 'Lay By', ordered = False)
            today_layby_payments = Payment.objects.filter(order__id__in = orders_r, order_type = 'Lay By', updated_at__gte = today)
            
         
        elif report_period == 2:
            ordered_items = yesterday_ordered_items(item_cat)
            report_period = "Yesterday"
            date_today = datetime.now().date()

            payments = Payment.objects.filter(updated_at__gte = yesterday,updated_at__lt = date_today)

            orders_r = Order.objects.filter(ordered = False)

            sum_total_vat = Money(0.0, 'MWK')
            orders = Order.objects.filter(ordered = True, updated_at__gte = yesterday,updated_at__lt = date_today)
            for order in orders:
                sum_total_vat += order.vat_cost
  
        elif report_period == 3:
            ordered_items = last_7_days_ordered_items(item_cat)
            report_period = "Last 7 Days"

            date_today = datetime.now().date()
            seven_days_b4 = date_today-timedelta(days=7)

            payments = Payment.objects.filter(updated_at__range = [seven_days_b4, date_today])

            orders_r = Order.objects.filter(ordered = False)
            sum_total_vat = Money(0.0, 'MWK')
            orders = Order.objects.filter(ordered = True, updated_at__range = [seven_days_b4, date_today])
            for order in orders:
                sum_total_vat += order.vat_cost
            
        elif report_period == 4:
            ordered_items= last_30_days_ordered_items(item_cat)
            report_period = "Last 30 Days"

            date_today = datetime.now().date()
            thirty_days_b4 = date_today-timedelta(days=30)

            payments = Payment.objects.filter(updated_at__range = [thirty_days_b4, date_today])

            orders_r = Order.objects.filter(ordered = False)
            
            sum_total_vat = Money(0.0, 'MWK')
            orders = Order.objects.filter(ordered = True, updated_at__range = [thirty_days_b4, date_today])
            for order in orders:
                sum_total_vat += order.vat_cost

        elif report_period == 5:
            ordered_items = this_month_ordered_items(item_cat)
            report_period = "This Month"
            
            today = datetime.now()
            this_month_firstday = datetime.now().date().replace(day=1)
        
            payments = Payment.objects.filter(updated_at__range = [this_month_firstday, today])

            orders_r = Order.objects.filter(ordered = False)

            sum_total_vat = Money(0.0, 'MWK')
            orders = Order.objects.filter(ordered = True, updated_at__range = [this_month_firstday, today])
            for order in orders:
                sum_total_vat += order.vat_cost

        elif report_period == 6:
            ordered_items = last_month_ordered_items(item_cat)
            report_period = "Last Month"

            today = datetime.now().date()
            this_month_firstday = today.replace(day=1)
            last_monthlastday = this_month_firstday - timedelta(days=1)
            last_monthlastday2 = last_monthlastday
            last_monthfirstday = last_monthlastday2.replace(day=1)

            payments = Payment.objects.filter(updated_at__range = [last_monthfirstday, last_monthlastday])

            orders_r = Order.objects.filter(ordered = False)
            
            sum_total_vat = Money(0.0, 'MWK')
            orders = Order.objects.filter(ordered = True, updated_at__range = [last_monthfirstday, last_monthlastday])
            for order in orders:
                sum_total_vat += order.vat_cost
    else:
        orders_r = Order.objects.filter(ordered = False)
    
    cash_payments = payments.filter(payment_mode = 'Cash')
    total_cash_payments = Money(0.0, 'MWK')
    for cash_payemnt in cash_payments:
        total_cash_payments += cash_payemnt.paid_amount
    
    bank_payments = payments.filter(payment_mode = 'Bank')
    total_bank_payments = Money(0.0, 'MWK')
    for bank_payment in bank_payments:
        total_bank_payments += bank_payment.paid_amount

    
    airtel_money_payments = payments.filter(payment_mode = 'Airtel Money')
    total_airtel_payments = Money(0.0, 'MWK')
    for airtel_money_payment in airtel_money_payments:
        total_airtel_payments += airtel_money_payment.paid_amount


    mpamba_payments = payments.filter(payment_mode = 'Mpamba')
    total_mpamba_payments = Money(0.0, 'MWK')
    for mpamba_payment in mpamba_payments:
        total_mpamba_payments += mpamba_payment.paid_amount
    
    sum_ordered_items_count = 0
    total_cost_items_ordered = Money(0.0, 'MWK') 
    for ordered_items_count in ordered_items:
        sum_ordered_items_count += ordered_items_count.quantity
        total_cost_items_ordered += ordered_items_count.ordered_items_total

    net_total_sales = total_cost_items_ordered - sum_total_vat

    
    total_cash_in_hand = total_mpamba_payments + total_airtel_payments + total_bank_payments + total_cash_payments


    context = {
        "header": 'sales report',
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
        "total_cash_in_hand":total_cash_in_hand,
        "report_time":report_time,

        "total_mpamba_payments":total_mpamba_payments,
        "total_cash_payments":total_cash_payments,
        "total_airtel_payments":total_airtel_payments,
        "total_bank_payments":total_bank_payments,
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

    sum_total_vat = Money(0.0, 'MWK')
    orders = Order.objects.filter(ordered = True)
    for order in orders:
        sum_total_vat += order.vat_cost

    report_time = timezone.now()

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
            payments = Payment.objects.filter(updated_at__gte = from_date, updated_at__lte = to_date)
            ordered_items = ordered_items.filter(ordered_time__gte = from_date, ordered_time__lte = to_date)


            sum_total_vat = Money(0.0, 'MWK')
            orders = Order.objects.filter(ordered = True, updated_at__gte = from_date, updated_at__lte = to_date)
            for order in orders:
                sum_total_vat += order.vat_cost
        
            orders_r = Order.objects.filter(ordered = False, updated_at__gte = from_date, updated_at__lte = to_date)

        lay_b_payments = Payment.objects.filter(order__id__in = orders_r, order_type = 'Lay By', updated_at__gte = from_date, updated_at__lte = to_date)

        sum_layby_paid_amount = Money(0.0, 'MWK')
        for lay_b_payments in lay_b_payments:
            if str(lay_b_payments.paid_amount) != "None":
                sum_layby_paid_amount += lay_b_payments.paid_amount
    else:
        lay_b_payments = Payment.objects.filter(order_type = 'Lay By')
        sum_layby_paid_amount = Money(0.0, 'MWK')
        for lay_b_payments in lay_b_payments:
            if str(lay_b_payments.paid_amount) != "None":
                sum_layby_paid_amount += lay_b_payments.paid_amount
        payments = Payment.objects.all()
    

    cash_payments = payments.filter(payment_mode = 'Cash')
    total_cash_payments = Money(0.0, 'MWK')
    for cash_payemnt in cash_payments:
        total_cash_payments += cash_payemnt.paid_amount
    
    bank_payments = payments.filter(payment_mode = 'Bank')
    total_bank_payments = Money(0.0, 'MWK')
    for bank_payment in bank_payments:
        total_bank_payments += bank_payment.paid_amount

    
    airtel_money_payments = payments.filter(payment_mode = 'Airtel Money')
    total_airtel_payments = Money(0.0, 'MWK')
    for airtel_money_payment in airtel_money_payments:
        total_airtel_payments += airtel_money_payment.paid_amount


    mpamba_payments = payments.filter(payment_mode = 'Mpamba')
    total_mpamba_payments = Money(0.0, 'MWK')
    for mpamba_payment in mpamba_payments:
        total_mpamba_payments += mpamba_payment.paid_amount

 
    sum_ordered_items_count = 0
    total_cost_items_ordered = Money(0.0, 'MWK') 
    for ordered_items_count in ordered_items:
        sum_ordered_items_count += ordered_items_count.quantity
        total_cost_items_ordered += ordered_items_count.ordered_items_total

    net_total_sales =  total_cost_items_ordered - sum_total_vat
    total_cash_in_hand = total_mpamba_payments + total_airtel_payments + total_bank_payments + total_cash_payments

    context = {
        "header": 'sales report',
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
        "report_time":report_time,

        "total_mpamba_payments":total_mpamba_payments,
        "total_cash_payments":total_cash_payments,
        "total_airtel_payments":total_airtel_payments,
        "total_bank_payments":total_bank_payments,
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
        return OrderItem.objects.filter(item__category__in = get_item_cat)
    else:
        return OrderItem.objects.all()

def todays_ordered_items(category):
    today = timezone.now().date()
    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)
    if get_item_cat.exists():
        return OrderItem.objects.filter(item__category__in = get_item_cat, ordered_time__gte = today)  
    else:
        return OrderItem.objects.filter(ordered_time__gte = today)

def yesterday_ordered_items(category):
    today = timezone.now().date()
    yesterday = today -timedelta(days=1)
    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)
    if get_item_cat.exists():
        return OrderItem.objects.filter(item__category__in = get_item_cat, ordered_time__range = [yesterday, today])
    else:
        return OrderItem.objects.filter(ordered_time__range = [yesterday, today])

def last_7_days_ordered_items(category):
    date_today = datetime.now().date()
    seven_days_b4 = date_today-timedelta(days=7)

    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)

    if get_item_cat.exists():
        return OrderItem.objects.filter(item__category__in = get_item_cat, ordered_time__range = [seven_days_b4, date_today])
    else:
        return OrderItem.objects.filter(ordered_time__range = [seven_days_b4, date_today])
def last_30_days_ordered_items(category):
    date_today = datetime.now().date()
    thirty_days_b4 = date_today-timedelta(days=30)
    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)
    if get_item_cat.exists():
        return OrderItem.objects.filter(item__category__in = get_item_cat, ordered_time__range = [thirty_days_b4, date_today])
    else:
        return OrderItem.objects.filter(ordered_time__range = [thirty_days_b4, date_today])
def this_month_ordered_items(category):
    today = datetime.now()
    this_month_firstday = datetime.now().date().replace(day=1)
    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)
    if get_item_cat.exists():
        return OrderItem.objects.filter(item__category__in = get_item_cat, ordered_time__range = [this_month_firstday, today])
    else:
       return OrderItem.objects.filter(ordered_time__range = [this_month_firstday, today])

def last_month_ordered_items(category):
    today = datetime.now().date()
    this_month_firstday = today.replace(day=1)
    last_monthlastday = this_month_firstday - timedelta(days=1)
    last_monthlastday2 = last_monthlastday
    last_monthfirstday = last_monthlastday2.replace(day=1)
    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)
    if get_item_cat.exists():
        return OrderItem.objects.filter(item__category__in = get_item_cat, ordered_time__range = [last_monthfirstday, last_monthlastday])
    else:
        return OrderItem.objects.filter(ordered_time__range = [last_monthfirstday, last_monthlastday])

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



def inventory_quantity_report(request):
    items = Item.get_all_items()

    expected_sum_items_cost = Money(0.0, 'MWK')
    sum_cost_of_goods = Money(0.0, 'MWK')
    for item in items:
        expected_sum_items_cost += item.get_expected_revenue()
        sum_cost_of_goods += item.get_total_cost_of_items()

    expected_profit = expected_sum_items_cost - sum_cost_of_goods


    item_cats = ItemCategory.get_all_item_categories()
    item_cat_id = request.GET.get('category')
  
    if item_cat_id != None:
        items = Item.get_all_items_by_category_id(item_cat_id)
    

    context = {
        'items': items,
        'header': 'Inventory quantity report',
        'item_cats': item_cats,
        'config':config,
        'expected_sum_items_cost':expected_sum_items_cost,
        'sum_cost_of_goods':sum_cost_of_goods,
        'expected_profit':expected_profit,
    }
    return render(request, 'inventory_reports/inventory_quantity_report.html', context)

def refund_report(request):
    item_cat = "All Categories"
    report_period = "All Days"

    total_items_refunded = Money(0.0, 'MWK')
    total_cost_items_refunded = Money('0.0', 'MWK')

    item_categories = ItemCategory.objects.all().order_by('category_name')

    refunded_items = all_days_refunds(report_period)

    today = timezone.now().date()
    report_time = timezone.now()
    yesterday = today-timedelta(days=1)


    if request.method == "POST":
        item_cat = request.POST.get('item_categories_option')
        report_period = request.POST.get('report_period')
        report_period = int(report_period)
        if report_period == 777:
            refunded_items = all_days_refunds(item_cat)
            report_period = "All Days"

        elif report_period == 1:
            refunded_items = todays_refunded_items(item_cat)
            report_period = "Today"

            refunded_payments_r = RefundPayment.objects.filter(updated_at__gte = today, refundorder__refunded = True)

           
        elif report_period == 2:
            refunded_items = yesterday_refunded_items(item_cat)
            report_period = "Yesterday"

            refunded_payments_r = RefundPayment.objects.filter(created_at__gte = yesterday,created_at__lt = today, refundorder__refunded = True)
  
        elif report_period == 3:
            refunded_items = last_7_days_refunded_items(item_cat)
            report_period = "Last 7 Days"
            date_today = datetime.now().date()
            seven_days_b4 = date_today-timedelta(days=7)
            refunded_payments_r = RefundPayment.objects.filter(updated_at__range = [seven_days_b4, date_today], refundorder__refunded = True)
           
        elif report_period == 4:
            refunded_items= last_30_days_refunded_items(item_cat)
            report_period = "Last 30 Days"
            date_today = datetime.now().date()
            thirty_days_b4 = date_today-timedelta(days=30)
            refunded_payments_r = RefundPayment.objects.filter(updated_at__range = [thirty_days_b4, date_today], refundorder__refunded = True)
           

        elif report_period == 5:
            refunded_items = this_month_refunded_items(item_cat)
            report_period = "This Month"
            today = datetime.now()
            this_month_firstday = datetime.now().date().replace(day=1)
            refunded_payments_r = RefundPayment.objects.filter(updated_at__range = [this_month_firstday, today], refundorder__refunded = True)
        

        elif report_period == 6:
            refunded_items = last_month_refunded_items(item_cat)
            report_period = "Last Month"
            today = datetime.now().date()
            this_month_firstday = today.replace(day=1)
            last_monthlastday = this_month_firstday - timedelta(days=1)
            last_monthlastday2 = last_monthlastday
            last_monthfirstday = last_monthlastday2.replace(day=1)
            refunded_payments_r = RefundPayment.objects.filter(updated_at__range = [last_monthfirstday, last_monthlastday], refundorder__refunded = True)
    else:
        refunded_payments_r = RefundPayment.objects.filter(refundorder__refunded = True)
    
    cash_refund_payments = refunded_payments_r.filter(payment_mode = 'Cash')
    total_cash_refund = Money(0.0, 'MWK')
    for cash_refund_payemnt in cash_refund_payments:
        total_cash_refund += cash_refund_payemnt.refund_amount
    
    bank_refund_payments = refunded_payments_r.filter(payment_mode = 'Bank')
    total_bank_refund = Money(0.0, 'MWK')
    for bank_refund_payment in bank_refund_payments:
        total_bank_refund += bank_refund_payment.refund_amount

    
    airtel_money_refund_payments = refunded_payments_r.filter(payment_mode = 'Airtel Money')
    total_airtel_refund = Money(0.0, 'MWK')
    for airtel_money_refund_payment in airtel_money_refund_payments:
        total_airtel_refund += airtel_money_refund_payment.refund_amount


    mpamba_refund_payments = refunded_payments_r.filter(payment_mode = 'Mpamba')
    total_mpamba_refund = Money(0.0, 'MWK')
    for mpamba_refund_payment in mpamba_refund_payments:
        total_mpamba_refund += mpamba_refund_payment.refund_amount
        
    sum_refunded_items_count = 0
    total_cost_items_refunded = Money(0.0, 'MWK') 
    for refunded_items_count in refunded_items:
        sum_refunded_items_count += refunded_items_count.return_quantity
        total_cost_items_refunded += refunded_items_count.return_items_total_cost

    total_refund_amount = total_cash_refund + total_bank_refund + total_airtel_refund + total_mpamba_refund

    

    context = {
        "header": "Refunds Report for " + " " + report_period,
        "item_cat":item_cat,
        "report_period":report_period,
        "item_categories":item_categories,
        "refunded_items":refunded_items,
        "total_items_refunded":total_items_refunded,
        "total_cost_items_refunded":total_cost_items_refunded,
        "config":config,
        "sum_refunded_items_count":sum_refunded_items_count,
        "total_refund_amount":total_refund_amount,
        "report_time":report_time,
        "total_cash_refund":total_cash_refund,
        "total_bank_refund":total_bank_refund,
        "total_airtel_refund":total_airtel_refund,
        "total_mpamba_refund":total_mpamba_refund,
    }
    return render(request, 'refunds_reports/refund_report.html', context)


def custom_range_refund_report(request):
    form = SearchBetweenTwoDatesForm()
    item_cat = "All Categories"
    
    total_items_refunded = 0
    total_cost_items_refunded = Money('0.0', 'MWK')

    item_categories = ItemCategory.objects.all().order_by('category_name')

    refunded_items = all_days_refunds(0)

    sum_total_vat = Money(0.0, 'MWK')
    orders = RefundOrder.objects.filter(ordered = True)
    for order in orders:
        sum_total_vat += order.vat_cost
    
    if request.method == "POST":
        if form.is_valid:
            from_date = request.POST.get('start_date_time')
            to_date = request.POST.get('end_date_time')
        
            item_cat = request.POST.get('item_categories_option')

        
        if is_valid_queryparam(from_date) and is_valid_queryparam(to_date):
            category_id = item_cat
            get_item_cat = ItemCategory.objects.filter(category_name = category_id)
            if get_item_cat.exists():
                refunded_items = refunded_items.filter(ordered_time__gte = from_date, ordered_time__lte = to_date, item__category__in = get_item_cat)
            refunded_items = refunded_items.filter(ordered_time__gte = from_date, ordered_time__lte = to_date)

            sum_total_vat = Money(0.0, 'MWK')
            orders = RefundOrder.objects.filter(ordered = True, updated_at__gte = from_date, updated_at__lte = to_date)
            for order in orders:
                sum_total_vat += order.vat_cost
        
        orders_r = RefundOrder.objects.filter(ordered = False)

    else:
        orders_r = RefundOrder.objects.filter(ordered = False)

    sum_refunded_items_count = 0
    total_cost_items_refunded = Money(0.0, 'MWK') 
    for refunded_items_count in refunded_items:
        sum_refunded_items_count += refunded_items_count.quantity
        total_cost_items_refunded += refunded_items_count.refunded_items_total

    net_total_sales =  total_cost_items_refunded - sum_total_vat
    total_cash_in_hand = total_cost_items_refunded + sum_layby_paid_amount

    report_time = timezone.now()

    context = {
        "item_cat":item_cat,
        "item_categories":item_categories,
        "form":form,
        "refunded_items":refunded_items,
        "total_items_refunded":total_items_refunded,
        "total_cost_items_refunded":total_cost_items_refunded,
        "config":config,
        "sum_refunded_items_count":sum_refunded_items_count,
        "sum_total_vat":sum_total_vat,
        "net_total_sales":net_total_sales,
        "sum_layby_paid_amount":sum_layby_paid_amount,
        "total_cash_in_hand":total_cash_in_hand,
    }
    return render(request, 'refunds_reports/custom_range_refund_report.html', context)

def all_days_refunds(category):
    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)
    if get_item_cat.exists():
        return RefundOrderItem.objects.filter(item__category__in = get_item_cat)
    else:
        return RefundOrderItem.objects.filter()

def todays_refunded_items(category):
    today = timezone.now().date()
    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)
    if get_item_cat.exists():
        return RefundOrderItem.objects.filter(item__item__category__in = get_item_cat, returned_time__gte = today)  
    else:
        return RefundOrderItem.objects.filter(returned_time__gte = today)


def yesterday_refunded_items(category):
    today = timezone.now().date()
    yesterday = today -timedelta(days=1)
    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)
    if get_item_cat.exists():
        return RefundOrderItem.objects.filter(item__item__category__in = get_item_cat, returned_time__range = [yesterday, today])
    else:
        return RefundOrderItem.objects.filter(returned_time__range = [yesterday, today])

def last_7_days_refunded_items(category):
    date_today = datetime.now().date()
    seven_days_b4 = date_today-timedelta(days=7)

    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)

    if get_item_cat.exists():
        return RefundOrderItem.objects.filter(item__item__category__in = get_item_cat, returned_time__range = [seven_days_b4, date_today])
    else:
        return RefundOrderItem.objects.filter(returned_time__range = [seven_days_b4, date_today])

def last_30_days_refunded_items(category):
    date_today = datetime.now().date()
    thirty_days_b4 = date_today-timedelta(days=30)
    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)
    if get_item_cat.exists():
        return RefundOrderItem.objects.filter(item__item__category__in = get_item_cat, returned_time__range = [thirty_days_b4, date_today])
    else:
        return RefundOrderItem.objects.filter(returned_time__range = [thirty_days_b4, date_today])

def this_month_refunded_items(category):
    today = datetime.now()
    this_month_firstday = datetime.now().date().replace(day=1)
    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)
    if get_item_cat.exists():
        return RefundOrderItem.objects.filter(item__item__category__in = get_item_cat, returned_time__range = [this_month_firstday, today])
    else:
       return RefundOrderItem.objects.filter(returned_time__range = [this_month_firstday, today])

def last_month_refunded_items(category):
    today = datetime.now().date()
    this_month_firstday = today.replace(day=1)
    last_monthlastday = this_month_firstday - timedelta(days=1)
    last_monthlastday2 = last_monthlastday
    last_monthfirstday = last_monthlastday2.replace(day=1)
    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)
    if get_item_cat.exists():
        return RefundOrderItem.objects.filter(item__item__category__in = get_item_cat, returned_time__range = [last_monthfirstday, last_monthlastday])
    else:
        return RefundOrderItem.objects.filter(returned_time__range = [last_monthfirstday, last_monthlastday])


def profit_report(request):
    today_start_day = datetime.now()
    item_cat = "All Categories"
    report_period = "All Days"
    ordered_items = all_days_sales(report_period)

    total_cost_items_ordered = Money('0.0', 'MWK')

    item_categories = ItemCategory.objects.all().order_by('category_name')

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
            expenses = Expense.objects.all()
            total_item_sold = get_summery_item_sales_all_days(today_start_day, item_cat)

        elif report_period == 1:
            total_item_sold = get_summery_item_sales_today(item_cat)
            ordered_items = todays_ordered_items(item_cat)
            report_period = "Today"
            expenses = Expense.objects.filter(created_at__gte = today)
            
        elif report_period == 2:
            total_item_sold = get_summery_item_sales_yesterday(item_cat)
            ordered_items = yesterday_ordered_items(item_cat)
            report_period = "Yesterday"
            date_today = datetime.now().date()
            expenses = Expense.objects.filter(created_at__gte = yesterday,created_at__lt = date_today)
        
        elif report_period == 3:
            total_item_sold = get_summery_item_sales_last_7_days(item_cat)
            ordered_items = last_7_days_ordered_items(item_cat)
            report_period = "Last 7 Days"
            date_today = datetime.now().date()
            seven_days_b4 = date_today-timedelta(days=7)
            expenses = Expense.objects.filter(created_at__range = [seven_days_b4, date_today])
            
        elif report_period == 4:
            total_item_sold = get_summery_item_sales_last_30_days(item_cat)
            ordered_items= last_30_days_ordered_items(item_cat)
            report_period = "Last 30 Days"
            date_today = datetime.now().date()
            thirty_days_b4 = date_today-timedelta(days=30)
            expenses = Expense.objects.filter(created_at__range = [thirty_days_b4, date_today])
        
        elif report_period == 5:
            total_item_sold = get_summery_item_sales_this_month(item_cat)
            ordered_items = this_month_ordered_items(item_cat)
            report_period = "This Month"
            today = datetime.now()
            this_month_firstday = datetime.now().date().replace(day=1)
            expenses = Expense.objects.filter(created_at__range = [this_month_firstday, today])
    
        elif report_period == 6:
            total_item_sold = get_summery_item_sales_last_month(item_cat)
            ordered_items = last_month_ordered_items(item_cat)
            report_period = "Last Month"

            today = datetime.now().date()
            this_month_firstday = today.replace(day=1)
            last_monthlastday = this_month_firstday - timedelta(days=1)
            last_monthlastday2 = last_monthlastday
            last_monthfirstday = last_monthlastday2.replace(day=1)

            expenses = Expense.objects.filter(created_at__range = [last_monthfirstday, last_monthlastday])
            
    else:
        expenses = Expense.objects.all()
        total_item_sold = get_summery_item_sales_all_days(today_start_day, item_cat)
        
    sum_expenses = Money(0.0, 'MWK')
    for expense in expenses:
        sum_expenses += expense.amount

    summery_expenses = get_sum_of_expenses_by_category(expenses)
    expense_list = view_expense_cat_list(expenses)


    sum_ordered_items_count = 0
    total_cost_items_ordered = Money(0.0, 'MWK')
    total_value_items_ordered = Money(0.0, 'MWK') 
    for ordered_items_count in ordered_items:
        sum_ordered_items_count += ordered_items_count.quantity
        total_cost_items_ordered += ordered_items_count.ordered_items_total
        total_value_items_ordered += ordered_items_count.quantity * ordered_items_count.item.cost_price
    
    
    gross_profit = get_profit(sum_expenses, total_cost_items_ordered, total_value_items_ordered )
    total_value_items_ordered += sum_expenses

    context = {
        "header":"Profit report",
        "item_cat":item_cat,
        "report_period":report_period,
        "item_categories":item_categories,
        "ordered_items":ordered_items,
        "total_item_sold":total_item_sold,
        "total_value_items_ordered":total_value_items_ordered,
        "summery_expenses":summery_expenses,
        "gross_profit":gross_profit,
        "total_cost_items_ordered":total_cost_items_ordered,
        "report_time":report_time,
        "sum_ordered_items_count":sum_ordered_items_count,
        "expense_list":expense_list,
    }
    return render(request, 'profit_reports/profit_report.html', context)

def get_summery_item_sales_all_days(todays_date, item_cat):
    category = item_cat
    todays_date = todays_date
    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)
    if get_item_cat.exists():
        item_cat_id = ItemCategory.objects.get(category_name = category_id)
        sales = Item.objects.filter(orderitem__ordered_time__lte = todays_date).filter(category = item_cat_id.id).values('item_name').annotate(total_quantity=Sum('orderitem__quantity')).annotate(sales_total = Sum('orderitem__ordered_items_total', output_field = MoneyOutput() )).annotate(cost_of_items = (Sum(F('orderitem__quantity') * F('cost_price'), output_field = MoneyOutput()))).annotate(profit = F('sales_total') - F('cost_of_items')) 
    else:
        sales = Item.objects.filter(orderitem__ordered_time__lte = todays_date).values('item_name').annotate(total_quantity=Sum('orderitem__quantity')).annotate(sales_total = Sum('orderitem__ordered_items_total', output_field = MoneyOutput() )).annotate(cost_of_items = (Sum(F('orderitem__quantity') * F('cost_price'), output_field = MoneyOutput()))).annotate(profit = F('sales_total') - F('cost_of_items')) 
    return sales

def get_summery_item_sales_today(category):
    today = timezone.now().date()
    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)
    if get_item_cat.exists():
        item_cat_id = ItemCategory.objects.get(category_name = category_id)
        return Item.objects.filter(category = item_cat_id.id, orderitem__ordered_time__gte = today).values('item_name').annotate(total_quantity=Sum('orderitem__quantity')).annotate(sales_total = Sum('orderitem__ordered_items_total', output_field = MoneyOutput() )).annotate(cost_of_items = (Sum(F('orderitem__quantity') * F('cost_price'), output_field = MoneyOutput()))).annotate(profit = F('sales_total') - F('cost_of_items')) 
    else:
        return Item.objects.filter(orderitem__ordered_time__gte = today).values('item_name').annotate(total_quantity=Sum('orderitem__quantity')).annotate(sales_total = Sum('orderitem__ordered_items_total', output_field = MoneyOutput() )).annotate(cost_of_items = (Sum(F('orderitem__quantity') * F('cost_price'), output_field = MoneyOutput()))).annotate(profit = F('sales_total') - F('cost_of_items'))

def get_summery_item_sales_yesterday(category):
    today = timezone.now().date()
    yesterday = today -timedelta(days=1)
    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)
    if get_item_cat.exists():
        item_cat_id = ItemCategory.objects.get(category_name = category_id)
        return Item.objects.filter(category = item_cat_id.id, orderitem__ordered_time__range = [yesterday, today]).values('item_name').annotate(total_quantity=Sum('orderitem__quantity')).annotate(sales_total = Sum('orderitem__ordered_items_total', output_field = MoneyOutput() )).annotate(cost_of_items = (Sum(F('orderitem__quantity') * F('cost_price'), output_field = MoneyOutput()))).annotate(profit = F('sales_total') - F('cost_of_items')) 
    else:
        return Item.objects.filter(orderitem__ordered_time__range = [yesterday, today]).values('item_name').annotate(total_quantity=Sum('orderitem__quantity')).annotate(sales_total = Sum('orderitem__ordered_items_total', output_field = MoneyOutput() )).annotate(cost_of_items = (Sum(F('orderitem__quantity') * F('cost_price'), output_field = MoneyOutput()))).annotate(profit = F('sales_total') - F('cost_of_items'))

def get_summery_item_sales_last_7_days(category):
    date_today = datetime.now().date()
    seven_days_b4 = date_today-timedelta(days=7)
    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)
    if get_item_cat.exists():
        item_cat_id = ItemCategory.objects.get(category_name = category_id)
        return Item.objects.filter(category = item_cat_id.id, orderitem__ordered_time__range = [seven_days_b4, date_today]).values('item_name').annotate(total_quantity=Sum('orderitem__quantity')).annotate(sales_total = Sum('orderitem__ordered_items_total', output_field = MoneyOutput() )).annotate(cost_of_items = (Sum(F('orderitem__quantity') * F('cost_price'), output_field = MoneyOutput()))).annotate(profit = F('sales_total') - F('cost_of_items')) 
    else:
        return Item.objects.filter(orderitem__ordered_time__range = [seven_days_b4, date_today]).values('item_name').annotate(total_quantity=Sum('orderitem__quantity')).annotate(sales_total = Sum('orderitem__ordered_items_total', output_field = MoneyOutput() )).annotate(cost_of_items = (Sum(F('orderitem__quantity') * F('cost_price'), output_field = MoneyOutput()))).annotate(profit = F('sales_total') - F('cost_of_items'))

def get_summery_item_sales_last_30_days(category):
    date_today = datetime.now().date()
    thirty_days_b4 = date_today-timedelta(days=30)
    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)
    if get_item_cat.exists():
        item_cat_id = ItemCategory.objects.get(category_name = category_id)
        return Item.objects.filter(category = item_cat_id.id, orderitem__ordered_time__range = [thirty_days_b4, date_today]).values('item_name').annotate(total_quantity=Sum('orderitem__quantity')).annotate(sales_total = Sum('orderitem__ordered_items_total', output_field = MoneyOutput() )).annotate(cost_of_items = (Sum(F('orderitem__quantity') * F('cost_price'), output_field = MoneyOutput()))).annotate(profit = F('sales_total') - F('cost_of_items')) 
    else:
        return Item.objects.filter(orderitem__ordered_time__range = [thirty_days_b4, date_today]).values('item_name').annotate(total_quantity=Sum('orderitem__quantity')).annotate(sales_total = Sum('orderitem__ordered_items_total', output_field = MoneyOutput() )).annotate(cost_of_items = (Sum(F('orderitem__quantity') * F('cost_price'), output_field = MoneyOutput()))).annotate(profit = F('sales_total') - F('cost_of_items'))

def get_summery_item_sales_this_month(category):
    today = datetime.now()
    this_month_firstday = datetime.now().date().replace(day=1)
    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)
    if get_item_cat.exists():
        item_cat_id = ItemCategory.objects.get(category_name = category_id)
        return Item.objects.filter(category = item_cat_id.id, orderitem__ordered_time__range = [this_month_firstday, today]).values('item_name').annotate(total_quantity=Sum('orderitem__quantity')).annotate(sales_total = Sum('orderitem__ordered_items_total', output_field = MoneyOutput() )).annotate(cost_of_items = (Sum(F('orderitem__quantity') * F('cost_price'), output_field = MoneyOutput()))).annotate(profit = F('sales_total') - F('cost_of_items')) 
    else:
        return Item.objects.filter(orderitem__ordered_time__range = [this_month_firstday, today]).values('item_name').annotate(total_quantity=Sum('orderitem__quantity')).annotate(sales_total = Sum('orderitem__ordered_items_total', output_field = MoneyOutput() )).annotate(cost_of_items = (Sum(F('orderitem__quantity') * F('cost_price'), output_field = MoneyOutput()))).annotate(profit = F('sales_total') - F('cost_of_items'))

def get_summery_item_sales_last_month(category):
    today = datetime.now().date()
    this_month_firstday = today.replace(day=1)
    last_monthlastday = this_month_firstday - timedelta(days=1)
    last_monthlastday2 = last_monthlastday
    last_monthfirstday = last_monthlastday2.replace(day=1)
    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)
    if get_item_cat.exists():
        item_cat_id = ItemCategory.objects.get(category_name = category_id)
        return Item.objects.filter(category = item_cat_id.id, orderitem__ordered_time__range = [last_monthfirstday, last_monthlastday]).values('item_name').annotate(total_quantity=Sum('orderitem__quantity')).annotate(sales_total = Sum('orderitem__ordered_items_total', output_field = MoneyOutput() )).annotate(cost_of_items = (Sum(F('orderitem__quantity') * F('cost_price'), output_field = MoneyOutput()))).annotate(profit = F('sales_total') - F('cost_of_items')) 
    else:
        return Item.objects.filter(orderitem__ordered_time__range = [last_monthfirstday, last_monthlastday]).values('item_name').annotate(total_quantity=Sum('orderitem__quantity')).annotate(sales_total = Sum('orderitem__ordered_items_total', output_field = MoneyOutput() )).annotate(cost_of_items = (Sum(F('orderitem__quantity') * F('cost_price'), output_field = MoneyOutput()))).annotate(profit = F('sales_total') - F('cost_of_items'))

def get_summery_item_sales_custom_dates(from_date, to_date, item_cat):
    from_date = from_date
    to_date = to_date
    category = item_cat
    category_id = str(category)
    get_item_cat = ItemCategory.objects.filter(category_name = category_id)
    if get_item_cat.exists():
        item_cat_id = ItemCategory.objects.get(category_name = category_id)
        sales = Item.objects.filter(orderitem__ordered_time__gte = from_date, orderitem__ordered_time__lte = to_date, category = item_cat_id.id).values('item_name').annotate(total_quantity=Sum('orderitem__quantity')).annotate(sales_total = Sum('orderitem__ordered_items_total', output_field = MoneyOutput() )).annotate(cost_of_items = (Sum(F('orderitem__quantity') * F('cost_price'), output_field = MoneyOutput()))).annotate(profit = F('sales_total') - F('cost_of_items')) 
    else:
        sales = Item.objects.filter(orderitem__ordered_time__gte = from_date, orderitem__ordered_time__lte = to_date).values('item_name').annotate(total_quantity=Sum('orderitem__quantity')).annotate(sales_total = Sum('orderitem__ordered_items_total', output_field = MoneyOutput() )).annotate(cost_of_items = (Sum(F('orderitem__quantity') * F('cost_price'), output_field = MoneyOutput()))).annotate(profit = F('sales_total') - F('cost_of_items')) 
    return sales

def custom_range_profit_report(request):
    form = SearchBetweenTwoDatesForm()
    item_cat = "All Categories"
    report_period = "All Days"
    report_time = timezone.now()

    item_categories = ItemCategory.objects.all().order_by('category_name')

    ordered_items = all_days_sales(0)
    today_start_day = datetime.now()
    
    total_item_sold = all_days_sales(0)

    if request.method == "POST":
        if form.is_valid:
            from_date = request.POST.get('start_date_time')
            to_date = request.POST.get('end_date_time')
            item_cat = request.POST.get('item_categories_option')

        if is_valid_queryparam(from_date) and is_valid_queryparam(to_date):
            category_id = item_cat
            get_item_cat = ItemCategory.objects.filter(category_name = category_id)
            if get_item_cat.exists():
                total_item_sold = get_summery_item_sales_custom_dates(from_date, to_date, item_cat)
                ordered_items = OrderItem.objects.filter(ordered_time__gte = from_date, ordered_time__lte = to_date, item__category__in = get_item_cat)
                expenses = Expense.objects.filter(created_at__gte = from_date, created_at__lte = to_date)
            else:
                ordered_items = OrderItem.objects.filter(ordered_time__gte = from_date, ordered_time__lte = to_date)
                expenses = Expense.objects.filter(created_at__gte = from_date, created_at__lte = to_date)
                total_item_sold = get_summery_item_sales_custom_dates(from_date, to_date, item_cat)
    else:
        expenses = Expense.objects.all()
        total_item_sold = get_summery_item_sales_all_days(today_start_day, item_cat)

    expenses_by_cat = get_sum_of_expenses_by_category(expenses)

    sum_expenses = Money(0.0, 'MWK')
    for expense in expenses:
        sum_expenses += expense.amount
    
    

    sum_ordered_items_count = 0
    total_cost_items_ordered = Money(0.0, 'MWK')
    total_value_items_ordered = Money(0.0, 'MWK') 
    for ordered_items_count in ordered_items:
        sum_ordered_items_count += ordered_items_count.quantity
        total_cost_items_ordered += ordered_items_count.ordered_items_total
        total_value_items_ordered += ordered_items_count.quantity * ordered_items_count.item.cost_price
    
    gross_profit = get_profit(sum_expenses, total_cost_items_ordered, total_value_items_ordered )
    total_value_items_ordered += sum_expenses
    context = {
        "header":"Profit report",
        "item_cat":item_cat,
        "report_period":report_period,
        "item_categories":item_categories,
        "ordered_items":ordered_items,
        "total_item_sold":total_item_sold,
        "total_value_items_ordered":total_value_items_ordered,
        "expenses_by_cat":expenses_by_cat,
        "gross_profit":gross_profit,
        "total_cost_items_ordered":total_cost_items_ordered,
        "report_time":report_time,
        "sum_ordered_items_count":sum_ordered_items_count,
        "form":form,
    }
    return render(request, 'profit_reports/custom_range_profit_report.html', context)

def get_sum_of_expenses_by_category(expenses):
    expenses_summery =  expenses.values('category__category_name','category__id').annotate(total_expense=Sum('amount', output_field = MoneyOutput()))
    return expenses_summery

def view_expense_cat_list(expenses):
    expenses_summery =  expenses.values('category__id','expense_description','amount','expense_name','created_at','payment_mode')
    return expenses_summery


def get_profit(expenses, sales_total, cost_of_sales):
    profit = Money(0.0, 'MWK')
    profit = sales_total - (expenses + cost_of_sales)
    return profit




