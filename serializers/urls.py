from django.urls import include, path
from rest_framework import routers
from serializers import views
# from tutorial.quickstart import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'orderitems', views.OrderItemViewSet)
router.register(r'items', views.ItemViewSet)
router.register(r'customers', views.CustomerViewSet)

router.register(r'customers', views.CustomerViewSet)
router.register(r'suppliers', views.SupplierViewSet)
router.register(r'itemcategories', views.ItemCategoryViewSet)
router.register(r'itemunits', views.ItemUnitsViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]