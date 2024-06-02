import http
import json
from django.shortcuts import HttpResponse
from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
import requests
import logging
from django.conf import settings
from urllib.parse import unquote

from pharma_gyan_proj.apps.pharma_gyan.auth_processor.auth_processor import validate_and_secure_login
from pharma_gyan_proj.apps.pharma_gyan.promo_code_processor.promo_code_processor import prepare_and_save_promo_code



@staff_member_required
@user_passes_test(lambda u: u.is_staff and u.groups.filter(name='pharma_gyan').exists())
def admin_login(request):
    baseUrl = settings.BASE_PATH
    rendered_page = render_to_string('pharma_gyan/login.html', {"baseUrl": baseUrl})
    resp = HttpResponse(rendered_page)
    resp.delete_cookie('access_token')
    return resp


@staff_member_required
@user_passes_test(lambda u: u.is_staff and u.groups.filter(name='pharma_gyan').exists())
def editor(request):
    rendered_page = render_to_string('pharma_gyan/base.html',
                                     {"tab_permissions": get_user_tab_permissions(request.user)})
    return HttpResponse(rendered_page)


@staff_member_required
@user_passes_test(lambda u: u.is_staff and u.groups.filter(name='pharma_gyan').exists())
@csrf_exempt
def dashboard(request):
    rendered_page = render_to_string('pharma_gyan/dashboard.html', {})
    return HttpResponse(rendered_page)


def get_user_tab_permissions(user):
    user_groups = [group.name for group in list(user.groups.all())]
    return user_groups


def promo_code(request):
    user = request.user

    rendered_page = render_to_string('pharma_gyan/add_promo_code.html', {"user": user})
    return HttpResponse(rendered_page)


def view_promo_code(request):
    user = request.user

    rendered_page = render_to_string('pharma_gyan/add_promo_code2.html', {"user": user})
    return HttpResponse(rendered_page)

def summernote(request):
    user = request.user

    rendered_page = render_to_string('pharma_gyan/summernote.html', {"user": user})
    return HttpResponse(rendered_page)

@csrf_exempt
def save_summernote(request):
    print('Summernote Before decode', request.body)
    # Extract the byte string from the request body
    byte_string = request.body  # This will be in byte format: b'data=...'

    # Decode the byte string to a regular string
    decoded_string = byte_string.decode('utf-8')  # Convert from bytes to string

    # Parse the URL-encoded data
    url_encoded_data = decoded_string.split('=', 1)[1]  # Get the part after 'data='

    # URL-decode the data
    decoded_data = unquote(url_encoded_data)
    print('Summernote After decode', decoded_data)
    return HttpResponse(json.dumps("{'data':'OK'}", default=str), status=http.HTTPStatus.OK, content_type="application/json")


@csrf_exempt
def upsert_promo_code(request):
    print('Before decode', request.body)
    # Extract the byte string from the request body
    byte_string = request.body  # This will be in byte format: b'data=...'

    # Decode the byte string to a regular string
    decoded_string = byte_string.decode('utf-8')  # Convert from bytes to string

    # Parse the URL-encoded data
    url_encoded_data = decoded_string.split('=', 1)[1]  # Get the part after 'data='

    # URL-decode the data
    decoded_data = unquote(url_encoded_data)
    print('After decode', decoded_data)
    request_body = json.loads(decoded_data)
    response = prepare_and_save_promo_code(request_body)
    status_code = response.pop("status_code", http.HTTPStatus.BAD_REQUEST)
    return HttpResponse(json.dumps(response, default=str), status=status_code, content_type="application/json")


@csrf_exempt
def secure_login(request):
    method_name = "secure_login"
    print(f'{method_name}, Before decode: {request.body}')
    request_body = json.loads(request.body.decode("utf-8"))
    response = validate_and_secure_login(request_body)
    status_code = response.pop("status_code", http.HTTPStatus.BAD_REQUEST)
    if status_code == http.HTTPStatus.OK:
        resp = HttpResponse(json.dumps(response, default=str), status=status_code, content_type="application/json")
        resp.set_cookie('access_token', response.get('access_token'))
        return resp
    return HttpResponse(json.dumps(response, default=str), status=status_code, content_type="application/json")