from django.urls import path
from django.contrib.auth import views as auth_views
from pos.views import *
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', pos_dashboard, name = 'pos_dashboard'), 
    path('view_order_items/<int:id>', view_order_items, name = 'view_order_items'),
    path('customers_list/', customers_list, name = 'customers_list'),
    path('personal_order_list/<int:id>', personal_order_list, name = 'personal_order_list'),

    path('add_to_cart/<slug>/', add_to_cart, name = 'add_to_cart'),
    path('remove_single_item_from_cart/<slug>/', remove_single_item_from_cart, name = 'remove_single_item_from_cart'),
    path('remove_from_cart/<slug>/', remove_from_cart, name = 'remove_from_cart'),
    path('save_bill/', save_bill, name = 'save_bill'),
    path('receipt/', receipt, name='receipt'),
    path('final_receipt/', final_receipt, name='final_receipt'),
    path('print_receipt_only/', print_receipt_only, name='print_receipt_only'),
    
    path('add_payment', add_payment, name = 'add_payment'),
    path('add_customer_to_order',add_customer_to_order, name='add_customer_to_order'),
    path('add_new_customer_from_pos_dash', add_new_customer_from_pos_dash, name = 'add_new_customer_from_pos_dash'),
    path('complete_order', complete_order, name = 'complete_order'),
    path('load_orders', load_orders, name = 'load_orders'),
    path('index', index, name='index'),

    path('view_my_orders', view_my_orders, name='view_my_orders'),
    path('view_all_orders', view_all_orders, name='view_all_orders'),



    path('supplier_list_pos/', supplier_list_pos, name = 'supplier_list_pos'),  
    path('customers/customer_list_pos/', customer_list_pos, name = 'customer_list_pos'),
    path('customers/customer_create_pos/', customer_create_pos, name = 'customer_create_pos'),
    path('customers/customer_update_pos/<int:id>/', customer_update_pos, name = 'customer_update_pos'),
    path('customers/customer_delete_pos/<int:id>/', customer_delete_pos, name = 'customer_delete_pos'),
    
    path('create_new_customer_on_pos_dash/', create_new_customer_on_pos_dash, name = 'create_new_customer_on_pos_dash'),
]