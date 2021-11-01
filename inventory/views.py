from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render,redirect, get_object_or_404
from inventory.models import ItemCategory, Unit, Item
from pos.models import Customer,OrderItem, Order
from inventory.forms import *
from pos.forms import *
from django.template.loader import render_to_string

from constance import config
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from serializers.serializers import *
# from constance.admin import ConstanceAdmin, ConstanceForm, Config

# Create your views here.
@login_required
def inventory_dashboard(request):
    total_item_categories = ItemCategory.objects.all().count()
    total_items = Item.objects.all().count()
    context = {
        'header':'Dashboard',
        'config':config,
        'total_item_categories':total_item_categories,
        'total_items':total_items,
        'config':config,
    }
    return render(request, 'inventory_dashboard.html', context)

@login_required
def item_list(request):
    items = Item.get_all_items()
    item_cats = ItemCategory.get_all_item_categories()
    item_cat_id = request.GET.get('category')
    print(item_cat_id)
    if item_cat_id != None:
        items = Item.get_all_items_by_category_id(item_cat_id)
    context = {
        'items': items,
        'header': 'Manage Items',
        'item_cats': item_cats,
        'config':config,
    }
    return render(request, 'items/items_list.html', context)

@login_required
def save_all_items(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            products =  Item.objects.all()
            print(products)
            # data['item_list'] = render_to_string('includes/items_list_2.html',{'products': products})
            data['item_list'] = render_to_string('items/items_list_2.html',{'products': products,})
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
            data['unit_list'] = render_to_string('includes/unit_list_2.html', {'units': units})
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