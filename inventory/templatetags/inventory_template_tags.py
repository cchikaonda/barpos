from django import template
from accounts.models import CustomUser
from inventory.models import *
from quotations.models import Quotation
from expenses.models import Expense, ExpenseCategory
from pos.models import Customer

register = template.Library()


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = Quotation.objects.filter(user=user, ordered = False)
        if qs.exists():
            return qs[0].items.count()
    return 0
    
@register.filter
def user_count(user):
    if user.is_authenticated:
        qs = CustomUser.objects.all().count()
    return qs

@register.filter
def item_category_count(user):
    if user.is_authenticated:
        qs = ItemCategory.objects.all().count()
    return qs

@register.filter
def item_count(user):
    if user.is_authenticated:
        qs = Item.objects.all().count()
    return qs

@register.filter
def unit_count(user):
    if user.is_authenticated:
        qs = Unit.objects.all().count()
    return qs

@register.filter
def supplier_count(user):
    if user.is_authenticated:
        qs = Supplier.objects.all().count()
    return qs

@register.filter
def stock_count(user):
    if user.is_authenticated:
        qs = Stock.objects.all().count()
    return qs

@register.filter
def batch_number_count(user):
    if user.is_authenticated:
        qs = BatchNumber.objects.all().count()
    return qs

@register.filter
def expenses_count(user):
    if user.is_authenticated:
        qs = Expense.objects.all().count()
    return qs

@register.filter
def customers_count(user):
    if user.is_authenticated:
        qs = Customer.objects.all().count()
    return qs


@register.filter
def expense_category_count(user):
    if user.is_authenticated:
        qs = ExpenseCategory.objects.all().count()
    return qs


@register.filter
def get_all_items_by_category_id(category_id):
    if category_id:
        return Expense.objects.filter(category=category_id).order_by('expense_name')
    else:
        return Expense.get_all_expense()