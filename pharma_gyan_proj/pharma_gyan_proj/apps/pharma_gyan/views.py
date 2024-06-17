import http
import json
from django.shortcuts import HttpResponse
from django.template.loader import render_to_string
# from django.contrib.admin.views.decorators import staff_member_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from urllib.parse import unquote

from pharma_gyan_proj.apps.pharma_gyan.auth_processor.auth_processor import validate_and_secure_login, \
    download_database_dump
from pharma_gyan_proj.apps.pharma_gyan.promo_code_processor.promo_code_processor import prepare_and_save_promo_code, \
    fetch_and_prepare_promo_code, fetch_promo_code_by_unique_id, deactivate_promo, activate_promo
from pharma_gyan_proj.common.constants import TAG_FAILURE, AdminUserPermissionType
from pharma_gyan_proj.apps.pharma_gyan.processors.user_processor import delete_user, fetch_and_prepare_users, fetch_user_from_id, fetch_users, prepare_and_save_user
from pharma_gyan_proj.apps.pharma_gyan.processors.course_processor import fetch_and_prepare_courses, prepare_and_save_course, process_activate_course, process_deactivate_course

import boto3

from django.http import JsonResponse
import json




def admin_login(request):
    baseUrl = settings.BASE_PATH
    rendered_page = render_to_string('pharma_gyan/login.html', {"baseUrl": baseUrl})
    resp = HttpResponse(rendered_page)
    resp.delete_cookie('access_token')
    return resp


def editor(request):
    rendered_page = render_to_string('pharma_gyan/base.html',
                                     {"tab_permissions": get_user_tab_permissions(request.user)})
    return HttpResponse(rendered_page)


@csrf_exempt
def dashboard(request):
    rendered_page = render_to_string('pharma_gyan/dashboard.html', {})
    return HttpResponse(rendered_page)


def get_user_tab_permissions(user):
    user_groups = [group.name for group in list(user.groups.all())]
    return user_groups


def promo_code(request):
    baseUrl = settings.BASE_PATH

    rendered_page = render_to_string('pharma_gyan/add_promo_code.html', {"baseUrl": baseUrl, "mode": "create"})
    return HttpResponse(rendered_page)


def edit_promo_code(request):
    baseUrl = settings.BASE_PATH
    # Retrieve the id parameter from the query string
    unique_id = request.GET.get('unique_id')
    promo_code = fetch_promo_code_by_unique_id(unique_id)
    if promo_code is None:
        response = dict(status_code=http.HTTPStatus.BAD_REQUEST, result=TAG_FAILURE, info="No promo code with this Id")
        return HttpResponse(json.dumps(response, default=str), status=response.status_code, content_type="application/json")
    print(promo_code)
    rendered_page = render_to_string('pharma_gyan/add_promo_code.html',
                                     {"promoCode": json.dumps(promo_code, default=str), "baseUrl": baseUrl, "mode": "edit"})
    return HttpResponse(rendered_page)


def view_promo_code(request):
    users = fetch_and_prepare_promo_code()
    # Convert list of dictionaries to JSON
    users_json = json.dumps(users)
    rendered_page = render_to_string('pharma_gyan/view_promo_code.html', {"users": users_json})
    return HttpResponse(rendered_page)

def summernote(request):
    user = request.user

    rendered_page = render_to_string('pharma_gyan/summernote.html', {"user": user})
    return HttpResponse(rendered_page)

@csrf_exempt
def save_summernote(request):
    # Extract the byte string from the request body
    byte_string = request.body  # This will be in byte format: b'data=...'

    # Decode the byte string to a regular string
    decoded_string = byte_string.decode('utf-8')  # Convert from bytes to string

    # Parse the URL-encoded data
    url_encoded_data = decoded_string.split('=', 1)[1]  # Get the part after 'data='

    # URL-decode the data
    decoded_data = unquote(url_encoded_data)
    return HttpResponse(json.dumps("{'data':'OK'}", default=str), status=http.HTTPStatus.OK, content_type="application/json")


@csrf_exempt
def upsert_promo_code(request):
    method_name = "upsert_promo_code"
    print(f'{method_name}, Before decode: {request.body}')
    request_body = json.loads(request.body.decode("utf-8"))
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


def dump_database(request):
    method_name = "dump_database"
    print(f'{method_name}, Before decode: {request.body}')
    response = download_database_dump()
    status_code = response.pop("status_code", http.HTTPStatus.BAD_REQUEST)
    return HttpResponse(json.dumps(response, default=str), status=status_code, content_type="application/json")


def addUser(request):
    user = request.user
    permissions = [(perm.name, perm.value) for perm in AdminUserPermissionType]
    rendered_page = render_to_string('pharma_gyan/add_user.html', {"user": user, "permissions": permissions, "mode": "create"})
    return HttpResponse(rendered_page)


def editUser(request):
    # Retrieve the id parameter from the query string
    user_id = request.GET.get('id')
    user = fetch_user_from_id(user_id)
    if user is None:
        response = dict(status_code=http.HTTPStatus.BAD_REQUEST, result=TAG_FAILURE, info="No user with this ID")
        return HttpResponse(json.dumps(response, default=str), status=response.status_code, content_type="application/json")
    permissions = [(perm.name, perm.value) for perm in AdminUserPermissionType]
    rendered_page = render_to_string('pharma_gyan/add_user.html', {"user": json.dumps(user, default=str), "permissions": permissions, "mode": "edit"})
    return HttpResponse(rendered_page)

def viewUsers(request):
    users = fetch_and_prepare_users()
    # Convert list of dictionaries to JSON
    users_json = json.dumps(users)
    rendered_page = render_to_string('pharma_gyan/view_users.html', {"users": users_json})
    return HttpResponse(rendered_page)

@csrf_exempt
def upsertUser(request):
    # Extract the byte string from the request body
    byte_string = request.body  # This will be in byte format: b'data=...'

    # Decode the byte string to a regular string
    decoded_string = byte_string.decode('utf-8')  # Convert from bytes to string

    # Parse the URL-encoded data
    url_encoded_data = decoded_string.split('=', 1)[1]  # Get the part after 'data='

    # URL-decode the data
    decoded_data = unquote(url_encoded_data)
    user = json.loads(decoded_data)
    response = prepare_and_save_user(user)
    status_code = response.pop("status_code", http.HTTPStatus.BAD_REQUEST)
    return HttpResponse(json.dumps(response, default=str), status=status_code, content_type="application/json")

@csrf_exempt
def deleteUser(request, userId):
    response = delete_user(userId)
    status_code = response.pop("status_code", http.HTTPStatus.BAD_REQUEST)
    return HttpResponse(json.dumps(response, default=str), status=status_code, content_type="application/json")


@csrf_exempt
def deactivate_promo_code(request, uniqueId):
    response = deactivate_promo(uniqueId)
    status_code = response.pop("status_code", http.HTTPStatus.BAD_REQUEST)
    return HttpResponse(json.dumps(response, default=str), status=status_code, content_type="application/json")


@csrf_exempt
def activate_promo_code(request, uniqueId):
    response = activate_promo(uniqueId)
    status_code = response.pop("status_code", http.HTTPStatus.BAD_REQUEST)
    return HttpResponse(json.dumps(response, default=str), status=status_code, content_type="application/json")

def addCourse(request):
    user = request.user
    rendered_page = render_to_string('pharma_gyan/add_course.html', {"user": user, "mode": "create"})
    return HttpResponse(rendered_page)

def viewCourses(request):
    courses = fetch_and_prepare_courses()
    # Convert list of dictionaries to JSON
    courses_json = json.dumps(courses)
    rendered_page = render_to_string('pharma_gyan/view_courses.html', {"courses": courses_json})
    return HttpResponse(rendered_page)

@csrf_exempt
def upsertCourse(request):
    title = request.POST.get('title')
    description = request.POST.get('description')
    image_file = request.FILES.get('image')
    
    imageUrl = save_file_to_s3(image_file)
    # Collect the data in a dictionary
    course = {
        'title': title,
        'description': description,
        'imageUrl': imageUrl,  # This is the uploaded file
    }
    
    response = prepare_and_save_course(course)
    status_code = response.pop("status_code", http.HTTPStatus.BAD_REQUEST)
    return HttpResponse(json.dumps(response, default=str), status=status_code, content_type="application/json")

def save_file_to_s3(file):
    s3_client = boto3.client(
        's3',
        aws_access_key_id="AKIAQ3EGS2LQMZK5DAFB",
        aws_secret_access_key="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",
        region_name="ap-south-1"
    )

    file_name = file.name

    s3_client.upload_fileobj(file, "pharma-gyan-test-media", file_name, ExtraArgs={'ACL': 'public-read'})

    s3_url = f"https://pharma-gyan-test-media.s3.ap-south-1.amazonaws.com/{file_name}"
    return s3_url

@csrf_exempt
def deactivate_course(request, uniqueId):
    response = process_deactivate_course(uniqueId)
    status_code = response.pop("status_code", http.HTTPStatus.BAD_REQUEST)
    return HttpResponse(json.dumps(response, default=str), status=status_code, content_type="application/json")


@csrf_exempt
def activate_course(request, uniqueId):
    response = process_activate_course(uniqueId)
    status_code = response.pop("status_code", http.HTTPStatus.BAD_REQUEST)
    return HttpResponse(json.dumps(response, default=str), status=status_code, content_type="application/json")