from django import template
from accounts.models import CustomUser
from inventory.models import *

register = template.Library()


# @register.filter
# def cart_item_count(user):
#     if user.is_authenticated:
#         qs = Order.objects.filter(user=user, ordered = False)
#         if qs.exists():
#             return qs[0].items.count()
#     return 0

# @register.filter
# def total_sales_query(user):
#     sales = Order.objects.filter(ordered = True).all()
#     total_sales = 0
#     for sales in sales:
#         total_sales += sales.get_total()
#     return total_sales

# @register.filter
# def expected_total_sale(user):
#     items = Item.objects.all()
#     expected_total_sale = 0
#     for item in items:
#         expected_total_sale += item.expected_total_sale
#     return expected_total_sale

     
# @register.filter
# def todays_sale(user):
#     today = datetime.datetime.today()
#     todays_sales = Order.objects.filter(ordered=True).filter(order_date = today)
#     todays_total_sales = Money('0.00','MWK')
#     for todays_s in todays_sales:
#         todays_total_sales += todays_s.get_after_tax_final_price()
#         return todays_total_sales
#     else:
#         return todays_total_sales
    
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