from django.urls import path
from django.contrib.auth import views as auth_views
from expenses.views import *
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('expense_list/', expense_list, name = 'expense_list'), 
    path('expense_category_create/', expense_category_create, name = 'expense_category_create'),
    path('expense_category_update/<int:id>/', expense_category_update, name = 'expense_category_update'),
    path('expense_category_delete/<int:id>/', expense_category_delete, name = 'expense_category_delete'),

    path('expense_categories/', expense_categories, name = 'expense_categories'),
    path('expense_create/', expense_create, name = 'expense_create'),
    path('expense_update/<int:id>/', expense_update, name = 'expense_update'),
    path('expense_delete/<int:id>/', expense_delete, name = 'expense_delete'),
    
]