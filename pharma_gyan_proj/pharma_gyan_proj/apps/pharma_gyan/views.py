import json
from django.shortcuts import HttpResponse
from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
import requests
import logging
from django.conf import settings


@staff_member_required
@user_passes_test(lambda u: u.is_staff and u.groups.filter(name='pharma_gyan').exists())
def editor(request):
    rendered_page = render_to_string('pharma_gyan/base.html',
                                     {"tab_permissions": get_user_tab_permissions(request.user)})
    return HttpResponse(rendered_page)


@staff_member_required
@user_passes_test(lambda u: u.is_staff and u.groups.filter(name='pharma_gyan').exists())
def dashboard(request):
    rendered_page = render_to_string('pharma_gyan/dashboard.html', {})
    return HttpResponse(rendered_page)


def get_user_tab_permissions(user):
    user_groups = [group.name for group in list(user.groups.all())]
    return user_groups
