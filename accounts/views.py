from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render,redirect, get_object_or_404
from inventory.models import ItemCategory, Supplier, Unit, Item
from pos.models import Customer, OrderItem, Order, RefundOrder, SessionTime
from constance import config
from django.db.models import Count
from quotations.models import Quotation
from .import decorators
from django.utils import timezone
from datetime import datetime

# Create your views here.
@login_required
def system_dashboard(request):
    session_time = SessionTime.objects.last()
    if session_time:
        open_time = session_time.open_time
        closing_time = session_time.closing_time
    suppliers_count = Supplier.objects.all().count()
    my_invoices_count = Order.objects.filter(user = request.user).count()
    all_invoices_count = Order.objects.all().count()
    count_my_invoices = Order.objects.filter(user = request.user, ordered = False).count()
    quotations_count = Quotation.objects.all().count()
    count_customers = Customer.objects.all().count()

    refunds_count = RefundOrder.objects.all().count()
    
    clock_out = timezone.now()
    context={
        'home':'Home',
        'header':'Home', 
        'config':config,
        'suppliers_count':suppliers_count,
        'my_invoices_count':my_invoices_count,
        'all_invoices_count':all_invoices_count,
        'config':config,
        'count_my_invoices':count_my_invoices,
        'quotations_count':quotations_count,
        'count_customers':count_customers,
        'refunds_count':refunds_count,
        'session_time':session_time,
        'clock_out':clock_out,
        }
    return render(request, 'system_dashboard.html', context)

@login_required
def logout_request(request):
    logout(request)
    response = redirect('logout')
    response.delete_cookie('modalShown')
    return response


