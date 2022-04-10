# -*- coding: utf-8 -*-
from importlib import import_module

from django.apps import AppConfig
from django.conf import settings


class DynamicFieldsApp(AppConfig):
    name = 'dynamic_fields'
    verbose_name = "Django Dynamic Form Fields"

    def ready(self):
        patch_urls()


def patch_urls():
    from distutils.version import StrictVersion
    import django

    urlpatterns_style = 1
    if StrictVersion(django.get_version()) < StrictVersion('2.0.0'):
        from django.conf.urls import include, url
        from django.core.urlresolvers import clear_url_caches, reverse, NoReverseMatch
    else:
        from django.urls import clear_url_caches, include, reverse, path, NoReverseMatch
        urlpatterns_style = 2

    try:
        reverse('dynamic_fields:choices')
    except NoReverseMatch:
        urlconf_module = import_module(settings.ROOT_URLCONF)

        if urlpatterns_style == 1:
            urlconf_module.urlpatterns = [
                url(r'^dynamic_fields/', include('dynamic_fields.urls')),
            ] + urlconf_module.urlpatterns
        else:
            urlconf_module.urlpatterns = [
                path('dynamic_fields/', include('dynamic_fields.urls')),
            ] + urlconf_module.urlpatterns

        clear_url_caches()
