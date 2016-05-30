from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings


def conf_settings(request):
    return {'settings': settings}


def current_site(request):
    return {'current_site': get_current_site(request)}
