import http
import logging
import os
import uuid

from pharma_gyan_proj.apps.pharma_gyan.processors.chapter_processor import prepare_and_save_chapter, \
    fetch_and_prepare_chapter_view
from pharma_gyan_proj.apps.pharma_gyan.processors.chapter_processor import prepare_and_save_chapter, \
    fetch_and_prepare_chapters, deactivate_chapter_view, activate_chapter_view, fetch_chapter_by_unique_id, \
    fetch_chapter_by_id, fetch_and_prepare_chapter_preview_by_id
from pharma_gyan_proj.apps.pharma_gyan.processors.entity_tag_processor import fetch_and_prepare_entity_tag, \
    prepare_and_save_entity_tag, deactivate_entity, activate_entity, fetch_entity_tag_by_unique_id
from pharma_gyan_proj.apps.pharma_gyan.processors.tag_category_processor import fetch_and_prepare_tag_category
from pharma_gyan_proj.exceptions.failure_exceptions import InternalServerError
from pharma_gyan_proj.apps.pharma_gyan.processors.tag_category_processor import fetch_and_prepare_tag_category, fetch_and_prepare_tag_category_with_tags

from pharma_gyan_proj.apps.pharma_gyan.processors.package_processor import fetch_and_prepare_packages, fetch_package_from_id, prepare_and_save_package, process_activate_package, process_deactivate_package
from pharma_gyan_proj.utils.s3_utils import S3Wrapper

from pharma_gyan_proj.apps.pharma_gyan.processors.chapter_processor import fetch_and_prepare_chapter_preview

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
import boto3
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
from pharma_gyan_proj.common.constants import TAG_FAILURE, AdminUserPermissionType, TAG_SUCCESS, BUCKET_NAME, \
    ACTIVE_CHAPTER_CHECK
from pharma_gyan_proj.apps.pharma_gyan.processors.user_processor import delete_user, fetch_and_prepare_users, fetch_user_from_id, fetch_users, prepare_and_save_user
from pharma_gyan_proj.apps.pharma_gyan.processors.course_processor import fetch_and_prepare_courses, fetch_course_from_id, fetch_course_tree_from_id, prepare_and_save_course, process_activate_course, process_deactivate_course

from pharma_gyan_proj.apps.pharma_gyan.processors.course_processor import fetch_and_prepare_courses, prepare_and_save_course, process_activate_course, process_deactivate_course
import boto3
from django.http import JsonResponse
import json

from pharma_gyan_proj.apps.pharma_gyan.processors.course_processor_v2 import fetch_all_courses, fetch_and_prepare_courses_v2, fetch_course_from_id_v2, prepare_and_save_course_v2, process_activate_course_v2, process_deactivate_course_v2

from pharma_gyan_proj.middlewares.HttpRequestInterceptor import Session
from pharma_gyan_proj.apps.pharma_gyan.processors.unit_processor import fetch_unit_from_id, prepare_and_save_unit, \
    prepare_and_save_topic, fetch_and_prepare_topic, fetch_topic_by_unique_id, process_activate_topic, \
    process_deactivate_topic

from django.views.decorators.csrf import csrf_exempt
import re

def validate_filename(filename):
    # Check if filename contains only alphanumeric characters and underscores
    return re.match(r'^[\w.-]+$', filename)

def admin_login(request):
    baseUrl = settings.BASE_PATH
    rendered_page = render_to_string('pharma_gyan/login.html', {"baseUrl": baseUrl})
    resp = HttpResponse(rendered_page)
    resp.delete_cookie('access_token')
    resp.delete_cookie('client_id')
    return resp


def editor(request):
    session = Session()
    project_permissions = session.get_admin_user_permissions()
    client_id = session.admin_user_session.client_id
    permissions_list = re.split(r'\s*,\s*', project_permissions)
    rendered_page = render_to_string('pharma_gyan/base.html',
                                     {"project_permissions": permissions_list,"client_id":client_id, "tab_permissions": get_user_tab_permissions(request.user)})
    return HttpResponse(rendered_page)


@csrf_exempt
def dashboard(request):
    rendered_page = render_to_string('pharma_gyan/dashboard.html', {})
    return HttpResponse(rendered_page)


@csrf_exempt
#upload video and images:
def add_media(request):
    image_size_limit = 5 * 1024 * 1024  # 5 MB in bytes
    video_size_limit = 5 * 1024 * 1024  # 5 MB in bytes

    if request.method == 'POST' and (request.FILES.getlist('image-file') or request.FILES.getlist('video-file')):
        uploaded_files = request.FILES.getlist('image-file') + request.FILES.getlist('video-file')
        file_urls = []
        for file in uploaded_files:
            if file.size > image_size_limit and file.content_type.startswith('image/'):
                return JsonResponse({'result': 'failure', 'error': 'Image size exceeds 5MB limit'}, status=400)
            elif file.size > video_size_limit and file.content_type.startswith('video/'):
                return JsonResponse({'result': 'failure', 'error': 'Video size exceeds 5MB limit'}, status=400)

            if not validate_filename(file.name):
                return JsonResponse({'result': 'failure',
                                     'error': 'Invalid filename. Only alphanumeric characters, underscores, dots, and dashes are allowed.'},
                                    status=400)
            file.name = uuid.uuid4().hex + '_' + file.name

            file_url = S3Wrapper().upload_and_return_s3_url(BUCKET_NAME, file)
            if file_url is None:
                pass
            else:
                file_urls.append(file_url)

        if len(file_urls) <1:
            return JsonResponse({'result': 'failure', 'detailed_message': 'failed to upload media'}, status=400)

        return JsonResponse({'result': 'success', 'data': {'file_urls': file_urls}}, status=200)
    else:
        return JsonResponse({'result': 'failure'}, status=400)


def get_user_tab_permissions(user):
    user_groups = [group.name for group in list(user.groups.all())]
    return user_groups


def promo_code(request):
    baseUrl = settings.BASE_PATH

    rendered_page = render_to_string('pharma_gyan/add_promo_code.html', {"baseUrl": baseUrl, "mode": "create"})
    return HttpResponse(rendered_page)


def entity_tag(request):
    baseUrl = settings.BASE_PATH
    tag_category = fetch_and_prepare_tag_category()
    tag_category_json = json.dumps(tag_category)
    rendered_page = render_to_string('pharma_gyan/add_entity_tag.html', {"baseUrl": baseUrl, "mode": "create", "tag_category": tag_category_json})
    return HttpResponse(rendered_page)


@csrf_exempt
def preview_chapter_content(request):
    method_name = "preview_chapter_content"
    print(f'{method_name}, Before decode: {request.body}')
    request_body = json.loads(request.body.decode("utf-8"))
    id = request_body.get('id')
    unique_id = request_body.get('unique_id')
    title = request_body.get('title')
    content = request_body.get('content')
    if unique_id is not None and unique_id != '':
        chapter = fetch_and_prepare_chapter_preview(unique_id)
    elif id is not None and id != '':
        chapter = fetch_and_prepare_chapter_preview_by_id(id)
    elif title is not None and content is not None:
        chapter = {
            "title": title,
            "content": content
        }
    else:
        return dict(status_code=http.HTTPStatus.BAD_REQUEST, result=TAG_FAILURE, info="Invalid request!")

    rendered_page = render_to_string('pharma_gyan/preview_chapter_content.html',{"chapter": json.dumps(chapter, default=str)})
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

def edit_chapter(request):
    baseUrl = settings.BASE_PATH
    # Retrieve the id parameter from the query string
    id = request.GET.get('id')
    chapter = fetch_chapter_by_id(id)
    if chapter is None:
        response = dict(status_code=http.HTTPStatus.BAD_REQUEST, result=TAG_FAILURE, info="No chapter with this Id")
        return HttpResponse(json.dumps(response, default=str), status=response.status_code, content_type="application/json")
    rendered_page = render_to_string('pharma_gyan/summernote.html',
                                     {"edit_chapter": json.dumps(chapter, default=str), "baseUrl": baseUrl,"mode": "edit"})
    return HttpResponse(rendered_page)

def clone_entity_tag(request):
    baseUrl = settings.BASE_PATH
    # Retrieve the id parameter from the query string
    unique_id = request.GET.get('unique_id')
    entity_tag = fetch_entity_tag_by_unique_id(unique_id)
    if entity_tag is None:
        response = dict(status_code=http.HTTPStatus.BAD_REQUEST, result=TAG_FAILURE, info="No Entity tag with this Id")
        return HttpResponse(json.dumps(response, default=str), status=response.status_code, content_type="application/json")
    entity_tag_json = json.dumps(entity_tag)
    tag_category = fetch_and_prepare_tag_category()
    tag_category_json = json.dumps(tag_category)
    if tag_category_json is None:
        response = dict(status_code=http.HTTPStatus.BAD_REQUEST, result=TAG_FAILURE, info="No Entity tag category found!")
        return HttpResponse(json.dumps(response, default=str), status=response.status_code,
                            content_type="application/json")
    rendered_page = render_to_string('pharma_gyan/add_entity_tag.html',
                                     {"baseUrl": baseUrl, "mode": "clone", "entity_tag": entity_tag_json, "tag_category": tag_category_json})
    return HttpResponse(rendered_page)


def edit_or_clone_topic(request):
    baseUrl = settings.BASE_PATH
    # Retrieve the id parameter from the query string
    unique_id = request.GET.get('unique_id')
    mode = request.GET.get('mode')
    version = request.GET.get('version')
    topic = fetch_topic_by_unique_id(unique_id, version)
    if topic is None:
        response = dict(status_code=http.HTTPStatus.BAD_REQUEST, result=TAG_FAILURE, info="No Topic with this Id")
        return HttpResponse(json.dumps(response, default=str), status=response.status_code, content_type="application/json")

    chapters = fetch_and_prepare_chapter_view()
    if chapters is None or len(chapters) < 1:
        chapters = {}

    rendered_page = render_to_string('pharma_gyan/add_topic.html',
                                     {"baseUrl": baseUrl, "mode": mode, "topic_data": json.dumps(topic), "chapters": json.dumps(chapters)})
    return HttpResponse(rendered_page)

def clone_chapter(request):
    baseUrl = settings.BASE_PATH
    # Retrieve the id parameter from the query string
    id = request.GET.get('id')
    chapter = fetch_chapter_by_id(id)
    if chapter is None:
        response = dict(status_code=http.HTTPStatus.BAD_REQUEST, result=TAG_FAILURE, info="No chapter tag with this Id")
        return HttpResponse(json.dumps(response, default=str), status=response.status_code, content_type="application/json")
    chapter_json = json.dumps(chapter)
    rendered_page = render_to_string('pharma_gyan/summernote.html',
                                     {"baseUrl": baseUrl, "mode": "clone", "clone_chapter": chapter_json})
    return HttpResponse(rendered_page)


def view_promo_code(request):
    promo_code = fetch_and_prepare_promo_code()
    # Convert list of dictionaries to JSON
    promo_code_json = json.dumps(promo_code)
    rendered_page = render_to_string('pharma_gyan/view_promo_code.html', {"promo_code": promo_code_json, "project_permissions": Session().get_admin_user_permissions()})
    return HttpResponse(rendered_page)

def view_entity_tag(request):
    entity_tag = fetch_and_prepare_entity_tag()
    entity_tag_json = json.dumps(entity_tag)
    rendered_page = render_to_string('pharma_gyan/view_entity_tag.html', {"entity_tag": entity_tag_json, "project_permissions": Session().get_admin_user_permissions()})
    return HttpResponse(rendered_page)


def view_topic(request):
    topic = fetch_and_prepare_topic()
    rendered_page = render_to_string('pharma_gyan/view_topics.html', {"topic": json.dumps(topic), "project_permissions": Session().get_admin_user_permissions()})
    return HttpResponse(rendered_page)


def add_chapter(request):
    user = settings.BASE_PATH
    rendered_page = render_to_string('pharma_gyan/summernote.html', {"user": user, "mode": "save"})
    return HttpResponse(rendered_page)

def view_chapters(request):
    chapters = fetch_and_prepare_chapters()
    chapters_json = json.dumps(chapters)
    rendered_page = render_to_string('pharma_gyan/view_chapters.html', {"chapters": chapters_json, "project_permissions": Session().get_admin_user_permissions()})
    return HttpResponse(rendered_page)

@csrf_exempt
def upsert_chapter(request):
    method_name = "upsert_chapter"
    print(f'{method_name}, Before decode: {request.body}')
    request_body = json.loads(request.body.decode("utf-8"))
    response = prepare_and_save_chapter(request_body)
    status_code = response.pop("status_code", http.HTTPStatus.BAD_REQUEST)
    return HttpResponse(json.dumps(response, default=str), status=status_code, content_type="application/json")


@csrf_exempt
def upsert_topic_v2(request):
    method_name = "upsert_topic_v2"
    print(f'{method_name}, Before decode: {request.body}')
    request_body = json.loads(request.body.decode("utf-8"))
    response = prepare_and_save_topic(request_body)
    status_code = response.pop("status_code", http.HTTPStatus.BAD_REQUEST)
    return HttpResponse(json.dumps(response, default=str), status=status_code, content_type="application/json")

@csrf_exempt
def upsert_promo_code(request):
    method_name = "upsert_promo_code"
    print(f'{method_name}, Before decode: {request.body}')
    request_body = json.loads(request.body.decode("utf-8"))
    response = prepare_and_save_promo_code(request_body)
    status_code = response.pop("status_code", http.HTTPStatus.BAD_REQUEST)
    return HttpResponse(json.dumps(response, default=str), status=status_code, content_type="application/json")

@csrf_exempt
def upsert_entity_tag(request):
    method_name = "upsert_entity_tag"
    print(f'{method_name}, Before decode: {request.body}')
    request_body = json.loads(request.body.decode("utf-8"))
    response = prepare_and_save_entity_tag(request_body)
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
        resp.set_cookie('client_id', response.get('client_id'))
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
    rendered_page = render_to_string('pharma_gyan/view_users.html', {"users": users_json, "project_permissions": Session().get_admin_user_permissions()})
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
@csrf_exempt
def deactivate_entity_tag(request, uniqueId):
    response = deactivate_entity(uniqueId)
    status_code = response.pop("status_code", http.HTTPStatus.BAD_REQUEST)
    return HttpResponse(json.dumps(response, default=str), status=status_code, content_type="application/json")

@csrf_exempt
def activate_entity_tag(request, uniqueId):
    response = activate_entity(uniqueId)
    status_code = response.pop("status_code", http.HTTPStatus.BAD_REQUEST)
    return HttpResponse(json.dumps(response, default=str), status=status_code, content_type="application/json")

@csrf_exempt
def deactivate_chapter(request, uniqueId):
    response = deactivate_chapter_view(uniqueId)
    status_code = response.pop("status_code", http.HTTPStatus.BAD_REQUEST)
    return HttpResponse(json.dumps(response, default=str), status=status_code, content_type="application/json")

@csrf_exempt
def activate_chapter(request, uniqueId):
    response = activate_chapter_view(uniqueId)
    status_code = response.pop("status_code", http.HTTPStatus.BAD_REQUEST)
    return HttpResponse(json.dumps(response, default=str), status=status_code, content_type="application/json")

def addCourse(request):
    user = request.user
    json_file_path = os.path.join(os.path.dirname(__file__), 'mock', 'topics.json')
    topics = fetch_and_prepare_topic()
    tags = fetch_and_prepare_tag_category_with_tags()
    rendered_page = render_to_string('pharma_gyan/add_course_v2.html', {"user": user, "mode": "create", "topics": json.dumps(topics), "tags": json.dumps(tags)})
    return HttpResponse(rendered_page)

def addPackage(request):
    user = request.user
    courses = fetch_all_courses()
    rendered_page = render_to_string('pharma_gyan/add_package.html', {"user": user, "mode": "create", "courses": json.dumps(courses)})
    return HttpResponse(rendered_page)


def add_topic(request):
    user = request.user
    chapters = fetch_and_prepare_chapter_view(ACTIVE_CHAPTER_CHECK)
    rendered_page = render_to_string('pharma_gyan/add_topic.html', {"user": user, "mode": "create", "chapters": json.dumps(chapters)})
    return HttpResponse(rendered_page)

def editCourse(request):
    # Retrieve the id parameter from the query string
    course_id = request.GET.get('id')
    course = fetch_course_from_id(course_id)
    if course is None:
        response = dict(status_code=http.HTTPStatus.BAD_REQUEST, result=TAG_FAILURE, info="No course with this ID")
        return HttpResponse(json.dumps(response, default=str), status=response.status_code, content_type="application/json")
    rendered_page = render_to_string('pharma_gyan/add_course.html', {"course": course, "mode": "edit"})
    return HttpResponse(rendered_page)

def editCourseV2(request):
    # Retrieve the id parameter from the query string
    course_id = request.GET.get('id')
    course = fetch_course_from_id_v2(course_id)
    user = request.user
    topics = fetch_and_prepare_topic()
    tags = fetch_and_prepare_tag_category_with_tags()
    if course is None:
        response = dict(status_code=http.HTTPStatus.BAD_REQUEST, result=TAG_FAILURE, info="No course with this ID")
        return HttpResponse(json.dumps(response, default=str), status=http.HTTPStatus.BAD_REQUEST, content_type="application/json")
    print('course', json.dumps(course))
    rendered_page = render_to_string('pharma_gyan/add_course_v2.html', {"course": json.dumps(course),"mode": "edit", "topics": json.dumps(topics), "tags": json.dumps(tags)})
    return HttpResponse(rendered_page)

def cloneCourse(request):
    # Retrieve the id parameter from the query string
    course_id = request.GET.get('id')
    course = fetch_course_from_id_v2(course_id)
    topics = fetch_and_prepare_topic()
    tags = fetch_and_prepare_tag_category_with_tags()
    if course is None:
        response = dict(status_code=http.HTTPStatus.BAD_REQUEST, result=TAG_FAILURE, info="No course with this ID")
        return HttpResponse(json.dumps(response, default=str), status=http.HTTPStatus.BAD_REQUEST, content_type="application/json")
    rendered_page = render_to_string('pharma_gyan/add_course_v2.html', {"course": json.dumps(course),"mode": "clone", "topics": json.dumps(topics), "tags": json.dumps(tags)})
    return HttpResponse(rendered_page)

def editPackage(request):
    # Retrieve the id parameter from the query string
    package_id = request.GET.get('id')
    package = fetch_package_from_id(package_id)
    user = request.user
    courses = fetch_all_courses()
    if package is None:
        response = dict(status_code=http.HTTPStatus.BAD_REQUEST, result=TAG_FAILURE, info="No package with this ID")
        return HttpResponse(json.dumps(response, default=str), status=http.HTTPStatus.BAD_REQUEST, content_type="application/json")
    rendered_page = render_to_string('pharma_gyan/add_package.html', {"package": json.dumps(package),"mode": "edit", "courses": json.dumps(courses)})
    return HttpResponse(rendered_page)

def clonePackage(request):
    # Retrieve the id parameter from the query string
    package_id = request.GET.get('id')
    package = fetch_package_from_id(package_id)
    courses = fetch_all_courses()
    if package is None:
        response = dict(status_code=http.HTTPStatus.BAD_REQUEST, result=TAG_FAILURE, info="No package with this ID")
        return HttpResponse(json.dumps(response, default=str), status=http.HTTPStatus.BAD_REQUEST, content_type="application/json")
    rendered_page = render_to_string('pharma_gyan/add_package.html', {"package": json.dumps(package),"mode": "clone", "courses": json.dumps(courses)})
    return HttpResponse(rendered_page)

def viewCourses(request):
    courses = fetch_and_prepare_courses()
    # Convert list of dictionaries to JSON
    courses_json = json.dumps(courses)
    rendered_page = render_to_string('pharma_gyan/view_courses.html', {"courses": courses_json, "project_permissions": Session().get_admin_user_permissions()})
    return HttpResponse(rendered_page)

def viewCoursesV2(request):
    courses = fetch_and_prepare_courses_v2()
    # Convert list of dictionaries to JSON
    courses_json = json.dumps(courses)
    rendered_page = render_to_string('pharma_gyan/view_courses_v2.html', {"courses": courses_json, "project_permissions": Session().get_admin_user_permissions()})
    return HttpResponse(rendered_page)

def viewPackages(request):
    packages = fetch_and_prepare_packages()
    # Convert list of dictionaries to JSON
    packages_json = json.dumps(packages)
    rendered_page = render_to_string('pharma_gyan/view_packages.html', {"packages": packages_json, "project_permissions": Session().get_admin_user_permissions()})
    return HttpResponse(rendered_page)

@csrf_exempt
def upsertCourse(request):
    id = request.POST.get('id')
    unique_id = request.POST.get('unique_id')
    title = request.POST.get('title')
    description = request.POST.get('description')
    price = request.POST.get('price')
    image_file = request.FILES.get('image')
    semesters = json.loads(request.POST.get('semesters', '[]'))

    imageUrl = S3Wrapper().upload_and_return_s3_url(BUCKET_NAME, image_file)
    # Collect the data in a dictionary
    course = {
        'id': id,
        'unique_id': unique_id,
        'title': title,
        'description': description,
        'price': price,
        'imageUrl': imageUrl,  # This is the uploaded file
        'semesters': semesters,
    }

    response = prepare_and_save_course(course)
    status_code = response.pop("status_code", http.HTTPStatus.BAD_REQUEST)
    return HttpResponse(json.dumps(response, default=str), status=status_code, content_type="application/json")

@csrf_exempt
def upsertTopic(request):
    id = request.POST.get('id')
    unique_id = request.POST.get('unique_id')
    title = request.POST.get('title')
    chapters = json.loads(request.POST.get('chapters', '[]')) 
    
    topic = {
        'id': id,
        'unique_id': unique_id,
        'title': title,
        'chapters': chapters
    }
    print(topic)
    response = prepare_and_save_unit(topic)
    status_code = response.pop("status_code", http.HTTPStatus.BAD_REQUEST)
    return HttpResponse(json.dumps(response, default=str), status=status_code, content_type="application/json")

@csrf_exempt
def upsertCourseV2(request):
    course = json.loads(request.body.decode("utf-8"))
    print(course)
    response = prepare_and_save_course_v2(course)
    status_code = response.pop("status_code", http.HTTPStatus.BAD_REQUEST)
    return HttpResponse(json.dumps(response, default=str), status=status_code, content_type="application/json")

# upsertPackage
@csrf_exempt
def upsertPackage(request):
    unique_id = request.POST.get('unique_id')
    title = request.POST.get('title')
    description = request.POST.get('description')
    price = request.POST.get('price')
    image_file = request.FILES.get('image')
    courses = json.loads(request.POST.get('courses', '[]'))

    imageUrl = S3Wrapper().upload_and_return_s3_url(BUCKET_NAME, image_file)

    # Collect the data in a dictionary
    package = {
        'id': id,
        'unique_id': unique_id,
        'title': title,
        'description': description,
        'price': price,
        'imageUrl': imageUrl,  # This is the uploaded file
        'courses': courses,
    }
    response = prepare_and_save_package(package)
    status_code = response.pop("status_code", http.HTTPStatus.BAD_REQUEST)
    return HttpResponse(json.dumps(response, default=str), status=status_code, content_type="application/json")

def save_file_to_s3(file):
    s3_client = boto3.client(
        's3',
        aws_access_key_id="AKIAQUFLP6LRNCUHZSNH",
        aws_secret_access_key="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",
        region_name="ap-south-1"
    )

    file_name = file.name

    s3_client.upload_fileobj(file, "pharma-gyan-prod-media", file_name, ExtraArgs={'ACL': 'public-read'})

    s3_url = f"https://pharma-gyan-prod-media.s3.ap-south-1.amazonaws.com/{file_name}"
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

@csrf_exempt
def activate_course_v2(request):
    course_id = request.GET.get('id')
    response = process_activate_course_v2(course_id)
    status_code = response.pop("status_code", http.HTTPStatus.BAD_REQUEST)
    return HttpResponse(json.dumps(response, default=str), status=status_code, content_type="application/json")

@csrf_exempt
def deactivate_course_v2(request):
    course_id = request.GET.get('id')
    response = process_deactivate_course_v2(course_id)
    status_code = response.pop("status_code", http.HTTPStatus.BAD_REQUEST)
    return HttpResponse(json.dumps(response, default=str), status=status_code, content_type="application/json")

@csrf_exempt
def activate_package(request):
    course_id = request.GET.get('id')
    response = process_activate_package(course_id)
    status_code = response.pop("status_code", http.HTTPStatus.BAD_REQUEST)
    return HttpResponse(json.dumps(response, default=str), status=status_code, content_type="application/json")

@csrf_exempt
def deactivate_package(request):
    course_id = request.GET.get('id')
    response = process_deactivate_package(course_id)
    status_code = response.pop("status_code", http.HTTPStatus.BAD_REQUEST)
    return HttpResponse(json.dumps(response, default=str), status=status_code, content_type="application/json")

@csrf_exempt
def get_course_tree_json(request, uniqueId):
    response = fetch_course_tree_from_id(uniqueId)
    status_code = response.pop("status_code", http.HTTPStatus.BAD_REQUEST)
    return HttpResponse(json.dumps(response, default=str), status=status_code, content_type="application/json")

def addTopicChapters(request):
    topicId = request.GET.get('id')
    topic = fetch_unit_from_id(topicId)
    print(topic)
    rendered_page = render_to_string('pharma_gyan/add_topic_chapters.html', {"topic": topic, "mode": "create"})
    return HttpResponse(rendered_page)


@csrf_exempt
def activate_topic(request):
    request_body = json.loads(request.body.decode("utf-8"))
    unique_id = request_body.get('unique_id')
    version = request_body.get('version')
    response = process_activate_topic(unique_id, version)
    status_code = response.pop("status_code", http.HTTPStatus.BAD_REQUEST)
    return HttpResponse(json.dumps(response, default=str), status=status_code, content_type="application/json")


@csrf_exempt
def deactivate_topic(request):
    request_body = json.loads(request.body.decode("utf-8"))
    unique_id = request_body.get('unique_id')
    version = request_body.get('version')
    response = process_deactivate_topic(unique_id, version)
    status_code = response.pop("status_code", http.HTTPStatus.BAD_REQUEST)
    return HttpResponse(json.dumps(response, default=str), status=status_code, content_type="application/json")