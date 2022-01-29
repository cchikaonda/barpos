from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render,redirect, get_object_or_404
from inventory.models import ItemCategory, Unit, Item, Stock, Supplier
from pos.models import Customer,OrderItem, Order
from inventory.forms import *
from pos.forms import *
from django.template.loader import render_to_string

from constance import config
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from serializers.serializers import *
from django.db.models import AutoField,IntegerField,FloatField,ExpressionWrapper, F, DecimalField, Count, Sum
from djmoney.money import Money
from django.db.models.functions import TruncDay
from django.utils import timezone
from datetime import date, timedelta, datetime
from django.db.models.functions import Lower
from djmoney.models.fields import MoneyField



# Create your views here.
@login_required
def inventory_dashboard(request):
    supplier_count = Supplier.objects.all().count()
    total_item_categories = ItemCategory.objects.all().count()
    total_items = Item.objects.all().count()
    sales_all_time = Order.objects.all()

    total_cog = 0
    stocks = Stock.objects.all()
    for stock in stocks:
       total_cog += stock.get_total_cost_of_items

    total_cog_sold = 0
    ordered_items = OrderItem.objects.filter(ordered = True)

    for ordered_item in ordered_items:
        stock_o = Stock.objects.filter(item = ordered_item.item).order_by('-created_at')[0].ordered_price 

    for ordered_item in ordered_items:
       total_cog_sold += Stock.objects.filter(item = ordered_item.item).order_by('-created_at')[0].ordered_price * ordered_item.quantity
    
    total_tax = 0
    sales_overtime = 0
    for sales_all_time in sales_all_time:
        sales_overtime += sales_all_time.paid_amount.paid_amount
        total_tax += sales_all_time.vat_cost
    
    profit = sales_overtime -(total_tax + total_cog_sold) 

    monday_total_sales = get_total_sales_this_week(2)
    tuesday_total_sales = get_total_sales_this_week(3)
    wednesday_total_sales = get_total_sales_this_week(4)
    thursday_total_sales = get_total_sales_this_week(5)
    friday_total_sales = get_total_sales_this_week(6)
    saturday_total_sales = get_total_sales_this_week(7)
    sunday_total_sales = get_total_sales_this_week(1)
  

    lw_monday_total_sales = get_total_lastwk_sale(2)
    lw_tuesday_total_sales = get_total_lastwk_sale(3)
    lw_wednesday_total_sales = get_total_lastwk_sale(4)
    lw_thursday_total_sales = get_total_lastwk_sale(5)
    lw_friday_total_sales = get_total_lastwk_sale(6)
    lw_saturday_total_sales = get_total_lastwk_sale(7)
    lw_sunday_total_sales = get_total_lastwk_sale(1)

    #Getting items running out of stock
    items_run_out_of_stock = get_items_running_out_of_stock()
   

    context = {
        'header':'Dashboard',
        'config':config,
        'total_item_categories':total_item_categories,
        'total_items':total_items,
        'sales_overtime':sales_overtime,
        'config':config,

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

        'items_run_out_of_stock':items_run_out_of_stock,
        'total_cog':total_cog,
        'total_cog_sold':total_cog_sold,
        'profit':profit,
        'supplier_count':supplier_count,
        'total_tax':total_tax,

    }
    return render(request, 'inventory_dashboard.html', context)


def get_total_sales_this_week(this_day):
    week_start = date.today()
    
    week_start -= timedelta(days=week_start.weekday())
    week_end = week_start + timedelta(days=6)

    total_sales = Order.objects.filter(ordered = True, paid_amount__created_at__gte=week_start, paid_amount__created_at__lt=week_end).filter(
        paid_amount__created_at__week_day=this_day)
    sum_total_cost = 0
    for total_sales in total_sales:
        sum_total_cost += total_sales.paid_amount.paid_amount

    orders_r = Order.objects.filter(ordered = False)
    lay_by_orders = LayByOrders.objects.filter(order_id__in = orders_r)
    lay_b_payments = Payment.objects.filter(laybyorders__in = lay_by_orders, created_at__gte=week_start, created_at__lt=week_end, created_at__week_day=this_day)
    sum_layby_paid_amount = Money(0.0, 'MWK')
    for lay_b_payments in lay_b_payments:
        if str(lay_b_payments.paid_amount) != "None":
            sum_layby_paid_amount += lay_b_payments.paid_amount

    return sum_total_cost + sum_layby_paid_amount
    
def get_total_lastwk_sale(this_day_lw):
    some_day_last_week = date.today() - timedelta(days=7)
    monday_of_last_week = some_day_last_week - timedelta(days=(some_day_last_week.isocalendar()[2] - 1))
    monday_of_this_week = monday_of_last_week + timedelta(days=7)
    total_sales = Order.objects.filter(paid_amount__created_at__gte=monday_of_last_week,
                                                    paid_amount__created_at__lt=monday_of_this_week).filter(
    paid_amount__created_at__week_day = this_day_lw)
    sum_total_cost = 0
    for total_sales in total_sales:
        sum_total_cost += total_sales.paid_amount.paid_amount
    
    orders_r = Order.objects.filter(ordered = False)
    lay_by_orders = LayByOrders.objects.filter(order_id__in = orders_r)
    lay_b_payments = Payment.objects.filter(laybyorders__in = lay_by_orders, created_at__gte=monday_of_last_week, created_at__lt=monday_of_this_week, created_at__week_day=this_day_lw)
    sum_layby_paid_amount = Money(0.0, 'MWK')
    for lay_b_payments in lay_b_payments:
        if str(lay_b_payments.paid_amount) != "None":
            sum_layby_paid_amount += lay_b_payments.paid_amount

    return sum_total_cost

#items running out of stock
def get_items_running_out_of_stock():
    return Item.objects.filter(quantity_at_hand__lte = F('reorder_level'))

@login_required
def item_list(request):
    items = Item.get_all_items()

    expected_sum_items_cost = 0
    for item in items:
        expected_sum_items_cost += item.get_expected_revenue()

    item_cats = ItemCategory.get_all_item_categories()
    item_cat_id = request.GET.get('category')
    # print(item_cat_id)
    if item_cat_id != None:
        items = Item.get_all_items_by_category_id(item_cat_id)
    context = {
        'items': items,
        'header': 'Manage Items',
        'item_cats': item_cats,
        'config':config,
        'expected_sum_items_cost':expected_sum_items_cost,
    }
    return render(request, 'items/items_list.html', context)

@login_required
def save_all_items(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            items =  Item.objects.all()
            data['item_list'] = render_to_string('items/items_list_2.html',{'items': items,})
            print(data)
        else:
            data['form_is_valid'] = False
    context = {
        'form': form
    }
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)

@login_required
def item_create(request):
    if request.method == 'POST':
        form = AddItemForm(request.POST)
    else:
        form = AddItemForm()
    return save_all_items(request, form, 'items/item_create.html')

@login_required
def item_update(request, id):
    product = get_object_or_404(Item, id=id)
    if request.method == 'POST':
        form = AddItemForm(request.POST, instance=product)
    else:
        form = AddItemForm(instance=product)
    return save_all_items(request, form, 'items/item_update.html')

@login_required
def item_delete(request, id):
    data = dict()
    item = get_object_or_404(Item, id=id)
    if request.method == "POST":
        item.delete()
        data['form_is_valid'] = True
        items = Item.objects.all()
        data['item_list'] = render_to_string('items/item_list_2.html', {'items': items})
    else:
        context = {'item': item}
        data['html_form'] = render_to_string('items/item_delete.html', context, request=request)
    return JsonResponse(data)


@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    context = {
        'suppliers': suppliers,
        'header': 'Manage Suppliers',
        'config':config,
    }
    return render(request, 'suppliers/supplier_list.html', context)

@login_required
def save_all_suppliers(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            suppliers =  Supplier.objects.all()
            data['supplier_list'] = render_to_string('suppliers/supplier_list_2.html',{'suppliers': suppliers,})
        else:
            data['form_is_valid'] = False
    context = {
        'form': form
    }
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)

@login_required
def supplier_create(request):
    if request.method == 'POST':
        form = AddSupplierForm(request.POST)
    else:
        form = AddSupplierForm()
    return save_all_suppliers(request, form, 'suppliers/supplier_create.html')

@login_required
def supplier_update(request, id):
    supplier = get_object_or_404(Supplier, id=id)
    if request.method == 'POST':
        form = AddSupplierForm(request.POST, instance=supplier)
    else:
        form = AddSupplierForm(instance=supplier)
    return save_all_suppliers(request, form, 'suppliers/supplier_update.html')

@login_required
def supplier_delete(request, id):
    data = dict()
    supplier = get_object_or_404(Supplier, id=id)
    if request.method == "POST":
        supplier.delete()
        data['form_is_valid'] = True
        suppliers = Supplier.objects.all()
        data['supplier_list'] = render_to_string('suppliers/supplier_list_2.html', {'suppliers': suppliers})
    else:
        context = {'supplier': supplier}
        data['html_form'] = render_to_string('suppliers/supplier_delete.html', context, request=request)
    return JsonResponse(data)

@login_required
def category_list(request):
    items = Item.objects.all().order_by('item_name')
    item_cats = ItemCategory.objects.all().order_by('category_name')
    context = {
        'items': items,
        'header': 'Manage Item Categories',
        'item_cats': item_cats,
        'config':config,
    }
    return render(request, 'item_categories/category_list.html', context)

@login_required
def save_all_categories(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            item_cats = ItemCategory.objects.all()
            data['category_list'] = render_to_string('includes/category_list_2.html',{'item_cats': item_cats})
        else:
            data['form_is_valid'] = False
    context = {
        'form': form
    }
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)

@login_required
def category_create(request):
    if request.method == 'POST':
        form = AddCategoryForm(request.POST)
    else:
        form = AddCategoryForm()
    return save_all_categories(request, form, 'item_categories/category_create.html')

@login_required
def category_update(request, id):
    category = get_object_or_404(ItemCategory, id=id)
    if request.method == 'POST':
        form = AddCategoryForm(request.POST, instance=category)
    else:
        form = AddCategoryForm(instance=category)
    return save_all_categories(request, form, 'item_categories/category_update.html')

@login_required
def category_delete(request, id):
    data = dict()
    category = get_object_or_404(ItemCategory, id=id)
    if request.method == "POST":
        category.delete()
        data['form_is_valid'] = True
        item_cats = ItemCategory.objects.all()
        data['category_list'] = render_to_string('includes/category_list_2.html',{'item_cats': item_cats})
    else:
        context = {'category': category}
        data['html_form'] = render_to_string('item_categories/category_delete.html', context, request=request)
    return JsonResponse(data)

@login_required
def unit_list(request):
    units = Unit.objects.all().order_by('unit_description')
    context = {
        'header': 'Manage Item Units',
        'units': units,
        'config':config,
    }
    return render(request, 'units/unit_list.html', context)

@login_required
def save_unit_list(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            units = Unit.objects.all()
            data['unit_list'] = render_to_string('units/unit_list_2.html', {'units': units})
        else:
            data['form_is_valid'] = False
    context = {
        'form': form
    }
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)

@login_required
def unit_create(request):
    if request.method == 'POST':
        form = AddUnitForm(request.POST)
    else:
        form = AddUnitForm()
    return save_unit_list(request, form, 'units/unit_create.html')

@login_required
def unit_update(request, id):
    unit = get_object_or_404(Unit, id=id)
    if request.method == 'POST':
        form = AddUnitForm(request.POST, instance=unit)
    else:
        form = AddUnitForm(instance=unit)
    return save_unit_list(request, form, 'units/unit_update.html')

@login_required
def unit_delete(request, id):
    data = dict()
    unit = get_object_or_404(Unit, id=id)
    if request.method == "POST":
        unit.delete()
        data['form_is_valid'] = True
        units = Unit.objects.all()
        data['unit_list'] = render_to_string('units/unit_list_2.html', {'units': units})
    else:
        context = {'unit': unit}
        data['html_form'] = render_to_string('units/unit_delete.html', context, request=request)
    return JsonResponse(data)

@login_required
def user_list(request):
    # users = CustomUser.objects.exclude(email = request.user)
    users = CustomUser.objects.all()
    context = {
    'users': users,
    'header': 'Manage users',
    'config':config,
    }
    return render(request, 'users/user_list.html',context)

@login_required
def save_all_users(request,form,template_name):
	data = dict()
	if request.method == 'POST':
		if form.is_valid():
			form.save()
			data['form_is_valid'] = True
			users = CustomUser.objects.exclude(email = request.user)
			data['user_list'] = render_to_string('users/user_list_2.html',{'users':users})
		else:
			data['form_is_valid'] = False
	context = {
	'form':form
	}
	data['html_form'] = render_to_string(template_name,context,request=request)
	return JsonResponse(data)

@login_required
def user_create(request):
	if request.method == 'POST':
		form = UserAdminCreationForm(request.POST)
	else:
		form = UserAdminCreationForm()
	return save_all_users(request,form,'users/user_create.html')

@login_required
def user_update(request,id):
	user = get_object_or_404(CustomUser,id=id)
	if request.method == 'POST':
		form = EditUserPermissionsForm(request.POST,instance=user)
	else:
		form = EditUserPermissionsForm(instance=user)
	return save_all_users(request,form,'users/user_update.html')

@login_required
def user_delete(request,id):
	data = dict()
	user = get_object_or_404(CustomUser,id=id)
	if request.method == "POST":
		user.delete()
		data['form_is_valid'] = True
		users = CustomUser.objects.exclude(email = request.user)
		data['user_list'] = render_to_string('users/user_list_2.html',{'users':users})
	else:
		context = {'user':user}
		data['html_form'] = render_to_string('users/user_delete.html',context,request=request)
	return JsonResponse(data)

@login_required
def user_profile(request):
    user = request.user
    # print(user.full_name)
    form = EditProfileForm(instance = user)
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance = user)
        if form.is_valid():
            form.save()
            messages.success(request, "User Profile Successfully updated")
            
    context = {
        'form': form,
        'config':config,
    }
    return render(request, 'users/user_profile.html', context)

@login_required
def change_password(request):
    user = request.user
    form = ChangeUserPasswordForm(instance = user)
    if request.method == 'POST':
        form = ChangeUserPasswordForm(request.POST, request.FILES, instance = user)
        if form.is_valid():
            form.save()
    context = {
        'form': form,
        'config':config,
    }
    return render(request, 'users/change_password.html', context)


@login_required
def customer_list(request):
    customers = Customer.objects.all()
    context = {
        'customers': customers,
        'header': 'Manage Customers',
        'config':config,
    }
    return render(request, 'customers/customer_list.html', context)

@login_required
def save_customer_list(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            customers = Customer.objects.all()
            data['customer_list'] = render_to_string('customers/customer_list_2.html', {'customers': customers})
        else:
            data['form_is_valid'] = False
    context = {
        'form': form
    }
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)

@login_required
def customer_create(request):
    if request.method == 'POST':
        form = AddCustomerForm(request.POST)
    else:
        form = AddCustomerForm()
    return save_customer_list(request, form, 'customers/customer_create.html')

@login_required
def customer_update(request, id):
    customer = get_object_or_404(Customer, id=id)
    if request.method == 'POST':
        form = AddCustomerForm(request.POST, instance=customer)
    else:
        form = AddCustomerForm(instance=customer)
    return save_customer_list(request, form, 'customers/customer_update.html')

@login_required
def customer_delete(request, id):
    data = dict()
    customer = get_object_or_404(Customer, id=id)
    if request.method == "POST":
        customer.delete()
        data['form_is_valid'] = True
        customers = Customer.objects.all()
        data['customer_list'] = render_to_string('customers/customer_list_2.html', {'customers': customers})
    else:
        context = {'customer': customer}
        data['html_form'] = render_to_string('customers/customer_delete.html', context, request=request)
    return JsonResponse(data)


@login_required
def stock_list(request):
    ordered_items = OrderItem.objects.filter(ordered = True)

    for ordered_item in ordered_items:
        stock_o = Stock.objects.filter(item = ordered_item.item).order_by('-created_at')[0].ordered_price 

    stocks = Stock.objects.order_by('-created_at')
    stock_summery = Item.objects.prefetch_related('item_name').values('item_name','quantity_at_hand').annotate(sum_stock_in = Sum(F('stock__stock_in'))).annotate(total_ordered_price = Sum('stock__total_cost_of_items')).annotate(sum_sold = F('sum_stock_in')-F('quantity_at_hand'))    
    queryset = Item.objects.prefetch_related('item_name').values('item_name','quantity_at_hand').annotate(stock_in_sum = Sum(F('stock__stock_in'))).annotate(sum_sold = F('stock_in_sum')-F('quantity_at_hand'))
    print(queryset)

    # sold_items_total = Item.objects.filter(orderitem__ordered = True).values('item_name').annotate(total_quantity=Sum('orderitem__quantity'))
    # .annotate(sales_total = Sum('orderitem__ordered_items_total', output_field = FloatField() ))

    # print(sold_items_total)

    item_cats = ItemCategory.get_all_item_categories()
    item_cat_id = request.GET.get('category')
    if item_cat_id != None:
        stocks = Stock.objects.order_by('-created_at').filter(item__category = item_cat_id)
    context = {
        'stocks': stocks,
        'header': 'Manage Stocks',
        'config':config,
        'item_cats':item_cats,
        'stock_summery':stock_summery
    }
    return render(request, 'stocks/stock_list.html', context)

@login_required
def save_all_stocks(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            stocks =  Stock.objects.all()
            data['stock_list'] = render_to_string('stocks/stock_list_2.html',{'stocks': stocks,})
        else:
            data['form_is_valid'] = False
    context = {
        'form': form
    }
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)

@login_required
def stock_create(request):
    if request.method == 'POST':
        form = AddStockForm(request.POST)
    else:
        form = AddStockForm()
    return save_all_items(request, form, 'stocks/stock_create.html')

@login_required
def stock_delete(request, id):
    data = dict()
    stock = get_object_or_404(Stock, id=id)
    if request.method == "POST":
        item = Item.objects.get(id = stock.item.id)
        current_item_quantity = item.quantity_at_hand - stock.stock_in
        item.save()
        Item.objects.filter(id=item.id).update(quantity_at_hand = current_item_quantity)
        stock.delete()
        data['form_is_valid'] = True
        stocks = Stock.objects.all()
        data['stock_list'] = render_to_string('stocks/stock_list_2.html', {'stocks': stocks})
    else:
        context = {'stock': stock}
        data['html_form'] = render_to_string('stocks/stock_delete.html', context, request=request)
    return JsonResponse(data)
