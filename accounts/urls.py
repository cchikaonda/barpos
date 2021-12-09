from django.urls import path
from django.contrib.auth import views as auth_views
from accounts.views import *
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('system_dashboard/', system_dashboard, name = 'system_dashboard'),  
    path('', auth_views.LoginView.as_view(), name = 'login'),
    path('logout/', auth_views.LoginView.as_view(), name = 'logout'),
    path('logout_request', logout_request, name = 'logout_request'),
]