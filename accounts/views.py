from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render,redirect, get_object_or_404
from inventory.models import ItemCategory, Supplier, Unit, Item
from pos.models import Customer, OrderItem, Order
from constance import config

# Create your views here.
@login_required
def system_dashboard(request):
    suppliers_count = Supplier.objects.all().count()
    customers_count = Customer.objects.all().count()
    orders_count = Order.objects.filter(user=request.user).count()
    context={
        'home':'Home',
        'header':'Home', 
        'config':config,
        'suppliers_count':suppliers_count,
        'customers_count':customers_count,
        'orders_count':orders_count,
        }
    return render(request, 'system_dashboard.html', context)

@login_required
def logout_request(request):
    logout(request)
    response = redirect('logout')
    response.delete_cookie('modalShown')
    return response


