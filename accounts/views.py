from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render,redirect, get_object_or_404
from inventory.models import ItemCategory, Unit, Item
from pos.models import Customer, OrderItem, Order

# Create your views here.
@login_required
def system_dashboard(request):
    return render(request, 'system_dashboard.html', {'home':'Home','header':'Home'})

@login_required
def logout_request(request):
    logout(request)
    response = redirect('logout')
    response.delete_cookie('modalShown')
    return response


