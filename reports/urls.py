from django.urls import path
from django.contrib.auth import views as auth_views
from reports.views import *
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', reports_dashboard, name = 'reports_dashboard'), 
    path('sales_report', sales_report, name = 'sales_report'),
    path('sales_report_data', sales_report_data, name = 'sales_report_data'),
    path('summery_of_sales', summery_of_sales, name = 'summery_of_sales'),
    path('sales_report_custom_range', sales_report_custom_range, name = 'sales_report_custom_range'),
    path('inventory_quantity_report', inventory_quantity_report, name = 'inventory_quantity_report'),

    path('refund_report', refund_report, name = 'refund_report'),
    path('custom_range_refund_report', custom_range_refund_report, name = 'custom_range_refund_report'),

    path('profit_report', profit_report, name='profit_report'),
    

    
   
]