import http
import json
import logging
from urllib.parse import unquote_plus
import uuid
from datetime import datetime
from django.core.files.storage import FileSystemStorage

from pharma_gyan_proj.common.constants import TAG_FAILURE, TAG_SUCCESS, AdminUserPermissionType
from pharma_gyan_proj.exceptions.failure_exceptions import BadRequestException, InternalServerError
from pharma_gyan_proj.orm_models.v2.all_models import Package, PackageCourseMapping
from pharma_gyan_proj.db_models.course_model_v2 import course_model_v2
from pharma_gyan_proj.db_models.entity_tag import entity_tag_model
from pharma_gyan_proj.db_models.package_model import package_model
from pharma_gyan_proj.middlewares.HttpRequestInterceptor import Session

logger = logging.getLogger("apps")


def prepare_and_save_package(request_body):
    method_name = "prepare_and_save_package"
    logger.debug(f"Entry {method_name}, request_body: {request_body}")

    existing_package = get_package_by_title(request_body.get('title'))
    if existing_package is not None and len(existing_package) > 0:
        if existing_package[0].unique_id != request_body.get('unique_id'):
            return dict(status_code=http.HTTPStatus.CONFLICT, result=TAG_FAILURE,
                        details_message="Duplicate title found. Please use a different title.")

    package = Package()
    package.unique_id = uuid.uuid4().hex if request_body.get('unique_id') is None else request_body.get('unique_id')
    session = Session()
    package.client_id = session.admin_user_session.client_id
    package.title = request_body.get('title')
    package.description = request_body.get('description')
    package.price = request_body.get('price')
    package.thumbnail_url = request_body.get('imageUrl')

    filter_list = [{"column": "unique_id", "value": package.unique_id, "op": "=="}]
    version_count = package_model().fetch_count_by_filter(filter_list)
    package.version = version_count + 1
    
    if (request_body.get('ct')):
        package.ct = request_body.get('ct')

    for course_id in request_body.get('courses'):
        course_mapping = PackageCourseMapping(
            unique_id=str(uuid.uuid4()),
            version = 1,
            course_id=course_id
        )
        package.courses.append(course_mapping)

    save_or_update_package(package)
    
    logger.debug(f"Exit {method_name}, Success")
    return dict(status_code=http.HTTPStatus.OK, result=TAG_SUCCESS)

def get_package_by_title(title):
        filter_list = [{"column": "title", "value": title, "op": "=="}]
        return package_model().get_details_by_filter_list(filter_list=filter_list)

def save_or_update_package(package):
    method_name = "save_or_update_package"

    try:
        db_res = package_model().upsert(package)
        if not db_res.get("status"):
            raise InternalServerError(method_name=method_name,
                                      reason=db_res.get("response"))
    except InternalServerError as ey:
        logger.error(
            f"Error while saving or updating package InternalServerError ::{ey.reason}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    except Exception as e:
        logger.error(f"Error while saving or updating package ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)

    logger.debug(f"Exit {method_name}, Success")

def fetch_and_prepare_packages():
    method_name = "fetch_and_prepare_packages"
    logger.debug(f"Entry {method_name}")
    session = Session()
    client_id = session.admin_user_session.client_id
    filter_list = [{"column": "client_id", "value": client_id, "op": "=="}]
    packages = fetch_packages(filter_list)
    packages_list = []
    for package in packages:
        editBtn = "<button id=\"edit-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"editPackage('{}')\">Edit</button>".format(package.id, package.id)
        if package.is_active:
            cta = "<button id=\"deact-{}\" class=\"btn-outline-danger btn-sm mr-1\" onclick=\"deactivatePackage('{}')\">Deactivate</button>".format(
                package.id, package.id)
        else:
            cta = "<button id=\"act-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"activatePackage('{}')\">Activate</button>".format(
                package.id, package.id)
        packages_list.append({
            "id": package.id,
            "unique_id": package.unique_id,
            "title": package.title,
            "description": package.description,
            "price": float(package.price),
            "image_url": package.thumbnail_url,
            "course_count": len(package.courses),
            "is_active": package.is_active,
            "clone": "<button id=\"edit-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"clonePackage('{}')\">Clone</button>".format(package.id, package.id),
            "edit": editBtn,
            "cta": cta,
        })
    return packages_list

def fetch_package_from_id(package_id):
    print('fetch_package_from_id, package_id', package_id)
    session = Session()
    client_id = session.admin_user_session.client_id
    filter_list = [{"column": "id", "value": package_id, "op": "=="}, {"column": "client_id", "value": client_id, "op": "=="}]
    packages = fetch_packages(filter_list)
    if (len(packages) == 0):
        return None
    package = packages[0]
    print('package', package)
    course_json = package.to_json()
    return course_json

def fetch_packages(filter_list=[], relationships_list=[]):
    method_name = "fetch_courses"

    try:
        db_res = package_model().get_details_by_filter_list(filter_list, relationships_list = relationships_list)
    except InternalServerError as ey:
        logger.error(
            f"Error while fetching packages InternalServerError ::{ey.reason}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    except Exception as e:
        logger.error(f"Error while fetching packages ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)

    logger.debug(f"Exit {method_name}, Success")
    return db_res

def process_deactivate_package(package_id):
    method_name = "process_deactivate_package"

    try:
        session = Session()
        client_id = session.admin_user_session.client_id
        filter_list = [{"column": "id", "value": package_id, "op": "=="}, {"column": "client_id", "value": client_id, "op": "=="}]
        package_model().update_by_filter_list(filter_list, dict(is_active=0))
    except Exception as e:
        logger.error(f"Error while deactivating course ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)

    logger.debug(f"Exit {method_name}, Success")
    return dict(status_code=http.HTTPStatus.OK, result=TAG_SUCCESS)


def process_activate_package(package_id):
    method_name = "process_activate_package"

    try:
        session = Session()
        client_id = session.admin_user_session.client_id
        filter_list = [{"column": "id", "value": package_id, "op": "=="}, {"column": "client_id", "value": client_id, "op": "=="}]
        package_model().update_by_filter_list(filter_list, dict(is_active=1))
    except InternalServerError as ey:
        logger.error(
            f"Error while fetching package InternalServerError ::{ey.reason}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    except Exception as e:
        logger.error(f"Error while deleting package ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)

    logger.debug(f"Exit {method_name}, Success")
    return dict(status_code=http.HTTPStatus.OK, result=TAG_SUCCESS)