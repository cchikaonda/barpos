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
    
      
]