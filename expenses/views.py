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
def save_all_expense_categories(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            expense_categories =  ExpenseCategory.objects.all()
            messages.success(request, "Expense Category Processed!")
            data['expense_category_list'] = render_to_string('expenses/expense_categories_2.html',{'expense_categories': expense_categories,})
        else:
            data['form_is_valid'] = False
    context = {
        'form': form
    }
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)

@login_required
def expense_category_create(request):
    if request.method == 'POST':
        form = AddExpenseCategoryForm(request.POST)
    else:
        form = AddExpenseCategoryForm()
    return save_all_expense_categories(request, form, 'expenses/expense_category_create.html')

@login_required
def expense_category_update(request, id):
    expense_category = get_object_or_404(ExpenseCategory, id=id)
    if request.method == 'POST':
        form = AddExpenseCategoryForm(request.POST, instance=expense_category)
    else:
        form = AddExpenseCategoryForm(instance=expense_category)
    return save_all_expense_categories(request, form, 'expenses/expense_category_update.html')

@login_required
def expense_category_delete(request, id):
    data = dict()
    expense_category = get_object_or_404(ExpenseCategory, id=id)
    if request.method == "POST":
        expense_category.delete()
        data['form_is_valid'] = True
        expense_categories = ExpenseCategory.objects.all()
        messages.success(request, str(expense_category) + ' ' +  "Expense Category Deleted Successfully!")
        data['expense_category_list'] = render_to_string('expenses/expense_categories_2.html', {'expense_categories': expense_categories})
    else:
        context = {'expense_category': expense_category}
        data['html_form'] = render_to_string('expenses/expense_category_delete.html', context, request=request)
    return JsonResponse(data)


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
            messages.success(request, "Expense Processed!")
            data['expense_list'] = render_to_string('expenses/expense_list_2.html',{'expenses': expenses,})
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
        form = AddExpenseForm(request.POST, initial={"paid_by": request.user,})
    else:
        form = AddExpenseForm(initial={"paid_by": request.user})
    return save_all_expenses(request, form, 'expenses/expense_create.html')

@login_required
def expense_update(request, id):
    expense = get_object_or_404(Expense, id=id)
    if request.method == 'POST':
        form = AddExpenseForm(request.POST, instance=expense)
    else:
        form = AddExpenseForm(instance=expense)
    return save_all_expenses(request, form, 'expenses/expense_update.html')

@login_required
def expense_delete(request, id):
    data = dict()
    expense = get_object_or_404(Expense, id=id)
    if request.method == "POST":
        expense.delete()
        data['form_is_valid'] = True
        expenses = Expense.objects.all()
        messages.success(request, str(expense) + ' ' +  "Expense Deleted Successfully!")
        data['expense_list'] = render_to_string('expenses/expense_list_2.html', {'expenses': expenses})
    else:
        context = {'expense': expense}
        data['html_form'] = render_to_string('expenses/expense_delete.html', context, request=request)
    return JsonResponse(data)

