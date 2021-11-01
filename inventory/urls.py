from django.urls import path
from django.contrib.auth import views as auth_views
from inventory.views import *
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', inventory_dashboard, name = 'inventory_dashboard'),
    path('item_list/', item_list, name = 'items_list'),  
    path('item_create/', item_create, name = 'item_create'),
    path('item_update/<int:id>/', item_update, name = 'item_update'),
    path('item_delete/<int:id>/', item_delete, name = 'item_delete'),

    path('category_list/', category_list, name = 'category_list'),
    path('category_create/', category_create, name = 'category_create'),
    path('category_update/<int:id>/', category_update, name = 'category_update'),
    path('category_delete/<int:id>/', category_delete, name = 'category_delete'),

    path('unit_list/', unit_list, name = 'unit_list'),
    path('unit_create/', unit_create, name = 'unit_create'),
    path('unit_update/<int:id>/', unit_update, name = 'unit_update'),
    path('unit_delete/<int:id>/', unit_delete, name = 'unit_delete'),

    path('users/user_list/', user_list, name = 'user_list'),
    path('users/user_update/<int:id>/', user_update, name = 'user_update'),
    path('users/user_create/', user_create, name = 'user_create'),
    path('users/user_delete/<int:id>/', user_delete, name = 'user_delete'),
    path('users/user_profile/', user_profile, name = 'user_profile'),
    path('users/change_password/', change_password, name = 'change_password'),

    path('customers/customer_list/', customer_list, name = 'customer_list'),
    path('customers/customer_create/', customer_create, name = 'customer_create'),
    path('customers/customer_update/<int:id>/', customer_update, name = 'customer_update'),
    path('customers/customer_delete/<int:id>/', customer_delete, name = 'customer_delete'),

]