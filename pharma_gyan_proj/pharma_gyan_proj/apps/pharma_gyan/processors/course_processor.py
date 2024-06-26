import http
import json
import logging
from urllib.parse import unquote_plus
import uuid
from datetime import datetime
from django.core.files.storage import FileSystemStorage

from pharma_gyan_proj.common.constants import TAG_FAILURE, TAG_SUCCESS, AdminUserPermissionType
from pharma_gyan_proj.exceptions.failure_exceptions import BadRequestException, InternalServerError
from pharma_gyan_proj.db_models.course_model import course_model
from pharma_gyan_proj.orm_models.content_models import PgCourse, PgSemester, PgSubject, PgUnit, PgChapter

logger = logging.getLogger("apps")


def prepare_and_save_course(request_body):
    method_name = "prepare_and_save_course"
    logger.debug(f"Entry {method_name}, request_body: {request_body}")

    course = PgCourse()
    course.unique_id = uuid.uuid4().hex
    course.title = request_body.get('title')
    course.description = request_body.get('description')
    course.thumbnail_url = request_body.get('imageUrl')
    if (request_body.get('ct')):
        course.ct = request_body.get('ct')
        
    course.semesters = []
    semestersBody = request_body.get('semesters')
    for sem in semestersBody:
        semester = PgSemester()
        semester.unique_id = uuid.uuid4().hex
        semester.title = sem.get('semesterId')
        
        semester.subjects = []
        subjectBody = sem.get('subjects')
        for sub in subjectBody:
            subject = PgSubject()
            subject.unique_id = uuid.uuid4().hex
            subject.name = sub.get('title')
            subject.description = sub.get('description')
            
            subject.units = []
            unitBody = sub.get('topics')
            for topic in unitBody:
                unit = PgUnit()
                unit.unique_id = uuid.uuid4().hex
                unit.title = topic
                
                subject.units.append(unit)
            
            semester.subjects.append(subject)
            
        course.semesters.append(semester)
    
    save_or_update_course(course)
    
    logger.debug(f"Exit {method_name}, Success")
    return dict(status_code=http.HTTPStatus.OK, result=TAG_SUCCESS)

def save_or_update_course(course):
    method_name = "save_or_update_course"

    try:
        db_res = course_model().upsert(course)
        if not db_res.get("status"):
            raise InternalServerError(method_name=method_name,
                                      reason=db_res.get("response"))
    except InternalServerError as ey:
        logger.error(
            f"Error while saving or updating course InternalServerError ::{ey.reason}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    except Exception as e:
        logger.error(f"Error while saving or updating course ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)

    logger.debug(f"Exit {method_name}, Success")

def fetch_and_prepare_courses():
    method_name = "fetch_and_prepare_courses"
    logger.debug(f"Entry {method_name}")
    courses = fetch_courses()
    # Convert list of model instances to list of dictionaries
    courses_list = []
    for course in courses:
        if course.is_active:
            cta = "<button id=\"deact-{}\" class=\"btn-outline-danger btn-sm mr-1\" onclick=\"deactivateCourse('{}')\">Deactivate</button>".format(
                course.unique_id, course.unique_id)
        else:
            cta = "<button id=\"act-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"activateCourse('{}')\">Activate</button>".format(
                course.unique_id, course.unique_id)
        courses_list.append({
            "unique_id": course.unique_id,
            "title": course.title,
            "description": course.description,
            "image_url": course.thumbnail_url,
            "is_active": course.is_active,
            "cta": cta,
            # "is_active": user.is_active,
            # "edit": "<button id=\"edit-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"editUser('{}')\">Edit</button>".format(user.unique_id, user.unique_id),
            # "del": "<button id=\"del-{}\" class=\"btn-outline-danger btn-sm mr-1\" onclick=\"delUser('{}')\">Delete</button>".format(user.unique_id, user.unique_id)
        })
    return courses_list

def fetch_courses(filter_list=[]):
    method_name = "fetch_courses"

    try:
        db_res = course_model().get_details_by_filter_list(filter_list)
    except InternalServerError as ey:
        logger.error(
            f"Error while fetching courses InternalServerError ::{ey.reason}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    except Exception as e:
        logger.error(f"Error while fetching courses ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)

    logger.debug(f"Exit {method_name}, Success")
    return db_res

def process_deactivate_course(unique_id):
    method_name = "deactivate_promo"

    try:
        filter_list = [{"column": "unique_id", "value": unique_id, "op": "=="}]
        course_model().update_by_filter_list(filter_list, dict(is_active=0))
    except Exception as e:
        logger.error(f"Error while deactivating course ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)

    logger.debug(f"Exit {method_name}, Success")
    return dict(status_code=http.HTTPStatus.OK, result=TAG_SUCCESS)


def process_activate_course(unique_id):
    method_name = "activate_promo"

    try:
        filter_list = [{"column": "unique_id", "value": unique_id, "op": "=="}]
        course = course_model().get_details_by_filter_list(filter_list)
        if course is None or len(course) < 1:
            return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                        detailed_message="Course id is incorrect!")
        course_model().update_by_filter_list(filter_list, dict(is_active=1))
    except InternalServerError as ey:
        logger.error(
            f"Error while fetching courses InternalServerError ::{ey.reason}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    except Exception as e:
        logger.error(f"Error while deleting user ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)

    logger.debug(f"Exit {method_name}, Success")
    return dict(status_code=http.HTTPStatus.OK, result=TAG_SUCCESS)

# def fetch_user_from_id(course_id):
#     filter_list = [{"column": "unique_id", "value": course_id, "op": "=="}]
#     users = fetch_courses(filter_list)
#     if (len(users) == 0):
#         return None
#     user = users[0]
#     permissions = {permission.name: 0 for permission in AdminUserPermissionType}
#     set_permissions = set(user.permissions.split(', '))
#     for perm in set_permissions:
#         permissions[perm] = 1
#     # Convert list of model instances to list of dictionaries
#     users_list = []
#     for user in users:
#         users_list.append({
#             "id": user.id,
#             "unique_id": user.unique_id,
#             "display_name": user.display_name,
#             "email_id": user.email_id,
#             "user_name": user.user_name,
#             "mobile_number": user.mobile_number,
#             "password": user.password,
#             "permissions": permissions,
#             "is_active": user.is_active,
#             "ct": user.ct
#         })
#     return users_list[0]

# def delete_user(user_id):
#     method_name = "delete_user"

#     try:
#         filter_list = [{"column": "unique_id", "value": user_id, "op": "=="}]
#         db_res = admin_users_model().delete(filter_list)
#     except InternalServerError as ey:
#         logger.error(
#             f"Error while deleting user InternalServerError ::{ey.reason}")
#         return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
#     except Exception as e:
#         logger.error(f"Error while deleting user ::{e}")
#         return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)

#     logger.debug(f"Exit {method_name}, Success")
#     return dict(status_code=http.HTTPStatus.OK, result=TAG_SUCCESS)