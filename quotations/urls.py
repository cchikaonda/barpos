# from django.urls import path
# from django.contrib.auth import views as auth_views
# from quotations.views import *
# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.csrf import csrf_exempt

# urlpatterns = [
#     path('', quotation_dashboard, name = 'quotation_dashboard'),
#     # path('item_list/', item_list, name = 'items_list'),  
#     # path('item_create/', item_create, name = 'item_create'),
#     # path('item_update/<int:id>/', item_update, name = 'item_update'),
#     # path('item_delete/<int:id>/', item_delete, name = 'item_delete'),

#     # path('category_list/', category_list, name = 'category_list'),
#     # path('category_create/', category_create, name = 'category_create'),
#     # path('category_update/<int:id>/', category_update, name = 'category_update'),
#     # path('category_delete/<int:id>/', category_delete, name = 'category_delete'),

#     # path('unit_list/', unit_list, name = 'unit_list'),
#     # path('unit_create/', unit_create, name = 'unit_create'),
#     # path('unit_update/<int:id>/', unit_update, name = 'unit_update'),
#     # path('unit_delete/<int:id>/', unit_delete, name = 'unit_delete'),

#     # path('users/user_list/', user_list, name = 'user_list'),
#     # path('users/user_update/<int:id>/', user_update, name = 'user_update'),
#     # path('users/user_create/', user_create, name = 'user_create'),
#     # path('users/user_delete/<int:id>/', user_delete, name = 'user_delete'),
#     # path('users/user_profile/', user_profile, name = 'user_profile'),
#     # path('users/change_password/', change_password, name = 'change_password'),

#     # path('customers/customer_list/', customer_list, name = 'customer_list'),
#     # path('customers/customer_create/', customer_create, name = 'customer_create'),
#     # path('customers/customer_update/<int:id>/', customer_update, name = 'customer_update'),
#     # path('customers/customer_delete/<int:id>/', customer_delete, name = 'customer_delete'),

#     # path('stock_list/', stock_list, name = 'stock_list'),  
#     # path('stock_create/', stock_create, name = 'stock_create'),
#     # path('stock_delete/<int:id>/', stock_delete, name = 'stock_delete'),

#     # path('supplier_list/', supplier_list, name = 'supplier_list'),  
#     # path('supplier_create/', supplier_create, name = 'supplier_create'),
#     # path('supplier_update/<int:id>/', supplier_update, name = 'supplier_update'),
#     # path('supplier_delete/<int:id>/', supplier_delete, name = 'supplier_delete'),

# ]

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.views.decorators.csrf import csrf_exempt
from .views import (
    add_to_cart_quotation,
    remove_from_cart_quotation,
    suspend_order,
    add_customer_to_quotation,
    add_expire_date_to_quotation,
    quotation_summery,
    complete_quotation,
    remove_single_item_from_cart_quotation,
    add_customer,
) 
from django.views.decorators.csrf import csrf_exempt
from quotations.views import *

urlpatterns = [
    path('', csrf_exempt(views.quotation_dashboard), name = 'quotation_dashboard'),
    path('quotation/', views.quotation, name = 'quotation'),
    

    path('quotation_list/', views.quotation_list, name = 'quotation_list'),
    path('quotation_update/<int:id>/', views.quotation_update, name = 'quotation_update'),
    path('quotation_delete/<int:id>/', views.quotation_delete, name = 'quotation_delete'),


    path('quotation_summery/<int:id>/', quotation_summery, name = 'quotation_summery'),

    

    path('add_to_cart_quotation/<slug>/', add_to_cart_quotation, name = 'add_to_cart_quotation'),
    path('remove_single_item_from_cart_quotation/<slug>/', remove_single_item_from_cart_quotation, name = 'remove_single_item_from_cart_quotation'),
    path('remove_from_cart_quotation/<slug>/', remove_from_cart_quotation, name = 'remove_from_cart_quotation'),
    path('suspend_order/', suspend_order, name = 'suspend_order'),

    path('add_customer_to_quotation/', add_customer_to_quotation, name = 'add_customer_to_quotation'),
    path('change_markup/', views.change_markup, name = 'change_markup'),

    path('add_expire_date_to_quotation/', add_expire_date_to_quotation, name = 'add_expire_date_to_quotation'),
    
    path('add_customer/', add_customer, name = 'add_customer'),
    
    
    path('complete_quotation/', complete_quotation, name = 'complete_quotation'),
    
]
