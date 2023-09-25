# -*- coding: utf-8 -*-
from distutils.version import StrictVersion
import django

from dynamic_fields.views import DynamicFieldChoicesView


if StrictVersion(django.get_version()) < StrictVersion('2.0.0'):
    from django.conf.urls import url

    urlpatterns = [
        url(r'^choices/$', DynamicFieldChoicesView.as_view()),
    ]

else:
    from django.urls import path

    urlpatterns = [
        path('choices/', DynamicFieldChoicesView.as_view()),
    ]
