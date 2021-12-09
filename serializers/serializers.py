from accounts.models import CustomUser
from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models import fields
from django.db.models.query_utils import select_related_descend
from rest_framework import serializers
from django.contrib.auth import get_user_model
from inventory.models import Item, ItemCategory, Supplier, Unit
from pos.models import Order, OrderItem, Customer
from rest_framework.request import Request

User = get_user_model()


class UserSerializer(serializers.HyperlinkedModelSerializer):
    user_name = Customer.objects.all()
    class Meta:
        model = User
        fields = '__all__'
        # exclude = ['user']

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'


class ItemUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = '__all__'

class ItemCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    unit = ItemUnitSerializer()
    category = ItemCategorySerializer()
    class Meta:
        model = Item
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer()
    customer = CustomerSerializer()
    user = serializers.ReadOnlyField(source='user.full_name')
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many = True)
    class Meta:
        model = Order
        fields = '__all__'