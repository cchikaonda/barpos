from django.shortcuts import render,redirect, get_object_or_404
from inventory.models import ItemCategory, Unit, Item, Supplier
from pos.models import Customer, LayByOrders, OrderItem, Order, Payment
from django.contrib import messages
from constance import config
from django.utils import timezone
from datetime import date, timedelta, datetime
from django.core.exceptions import ObjectDoesNotExist
from pos.forms import AddPaymentForm, CashPaymentForm, SearchForm, AddCustomerForm, AddLayByPaymentForm
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.core import serializers
import json
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from accounts.admin import CustomConfigForm
from barpos import settings
import time
from djmoney.money import Money
from django.template.loader import render_to_string


from django.http import HttpResponse

import qrcode
import qrcode.image.svg
from io import BytesIO
from django.db.models.query import *



@login_required
def index(request):
    context = {}
    #generating QR Code
    if request.method == "POST":
        factory = qrcode.image.svg.SvgImage
        img = qrcode.make(request.POST.get("qr_text",""), image_factory=factory, box_size=20)
        stream = BytesIO()
        img.save(stream)
        context["svg"] = stream.getvalue().decode()
    return render(request, 'refunds_list.html', context=context)