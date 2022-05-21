from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render,redirect, get_object_or_404
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
from .forms import *
from .models import *




@login_required
def expense_categories(request):
    expense_categories = ExpenseCategory.objects.all()
    context = {
        'expense_categories': expense_categories,
        'header': 'Manage Expense Categories',
    }
    return render(request, 'expenses/expense_categories.html', context)

@login_required
def expense_list(request):
    expenses = Expense.objects.all()
    context = {
        'expenses': expenses,
        'header': 'Manage Expenses',
    }
    return render(request, 'expenses/expense_list.html', context)

@login_required
def save_all_expenses(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            expenses =  Expense.objects.all()
            data['expense_list'] = render_to_string('expenses/expense_list_2.html',{'expenses': expenses,})
            messages.success(request, "Expense Processed!")
        else:
            data['form_is_valid'] = False
    context = {
        'form': form
    }
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)

@login_required
def expense_create(request):
    if request.method == 'POST':
        form = AddExpenseForm(request.POST, initial={"paid_by": request.user.full_name})
    else:
        form = AddExpenseForm(initial={"paid_by": request.user.full_name})
    return save_all_expenses(request, form, 'expenses/expense_create.html')

@login_required
def expense_update(request, id):
    expense = get_object_or_404(Expense, id=id)
    if request.method == 'POST':
        form = AddExpenseForm(request.POST, instance=expense, initial={"paid_by": expense.paid_by.full_name})
    else:
        form = AddExpenseForm(instance=expense, initial={"paid_by": expense.paid_by.full_name})
    return save_all_expenses(request, form, 'expenses/expense_update.html')

@login_required
def expense_delete(request, id):
    data = dict()
    item = get_object_or_404(Expense, id=id)
    if request.method == "POST":
        item.delete()
        data['form_is_valid'] = True
        expenses = Expense.objects.all()
        data['expense_list'] = render_to_string('expenses/expense_list_2.html', {'expenses': expenses})
    else:
        context = {'item': item}
        data['html_form'] = render_to_string('expenses/item_delete.html', context, request=request)
    return JsonResponse(data)

