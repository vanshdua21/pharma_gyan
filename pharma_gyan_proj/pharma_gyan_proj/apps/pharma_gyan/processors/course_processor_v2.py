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
from pharma_gyan_proj.orm_models.v2.all_models import Course, CourseTagMapping, CourseTopicMapping
from pharma_gyan_proj.db_models.course_model_v2 import course_model_v2
from pharma_gyan_proj.db_models.entity_tag import entity_tag_model

logger = logging.getLogger("apps")


def prepare_and_save_course_v2(request_body):
    method_name = "prepare_and_save_course_v2"
    logger.debug(f"Entry {method_name}, request_body: {request_body}")

    course = Course()
    if (request_body.get('id')):
        course.id = request_body.get('id')
    course.unique_id = uuid.uuid4().hex if request_body.get('unique_id') is None else request_body.get('unique_id')
    course.client_id = 'cd6b7678-3ea3-11ef-a04f-5a57a4320fb5'
    course.title = request_body.get('title')
    course.description = request_body.get('description')
    course.version = 1
    
    if (request_body.get('ct')):
        course.ct = request_body.get('ct')

    for tag_id in request_body.get('tags'):
        tag_mapping = CourseTagMapping(
            unique_id=str(uuid.uuid4()),
            tag_id=tag_id
        )
        course.tags.append(tag_mapping)

    for order, topic_id in enumerate(request_body.get('topics'), start=1):
        topic_mapping = CourseTopicMapping(
            unique_id=str(uuid.uuid4()),
            topic_id=topic_id,
            order=order,
            version=1
        )
        course.topics.append(topic_mapping)

    save_or_update_course(course)
    
    logger.debug(f"Exit {method_name}, Success")
    return dict(status_code=http.HTTPStatus.OK, result=TAG_SUCCESS)

def save_or_update_course(course):
    method_name = "save_or_update_course"

    try:
        db_res = course_model_v2().upsert(course)
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

def fetch_and_prepare_courses_v2():
    method_name = "fetch_and_prepare_courses_v2"
    logger.debug(f"Entry {method_name}")
    # relationships_list = [Course.tags, CourseTagMapping.tag, Course.topics]
    courses = fetch_courses()
    # Convert list of model instances to list of dictionaries
    courses_list = []
    for course in courses:
        print('course', course)
        tag_ids = [tag.tag_id for tag in course.tags]
        filter_list = [{"column": "unique_id", "value": tag_ids, "op": "IN"}]
        tags = entity_tag_model().get_details_by_filter_list(filter_list=filter_list)
        print('tags', tags)
        editBtn = "<button id=\"edit-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"editCourse('{}')\">Edit</button>".format(course.unique_id, course.unique_id)
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
            "tags": [tag.title for tag in tags],
            "topics_count": len(course.topics),
            "is_active": course.is_active,
            "edit": editBtn,
            "cta": cta,
            # "is_active": user.is_active,
            # "edit": "<button id=\"edit-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"editUser('{}')\">Edit</button>".format(user.unique_id, user.unique_id),
            # "del": "<button id=\"del-{}\" class=\"btn-outline-danger btn-sm mr-1\" onclick=\"delUser('{}')\">Delete</button>".format(user.unique_id, user.unique_id)
        })
    return courses_list

def fetch_course_from_id_v2(course_id):
    print('fetch_course_from_id_v2, course_id', course_id)
    filter_list = [{"column": "unique_id", "value": course_id, "op": "=="}]
    courses = fetch_courses(filter_list)
    print('length', len(courses))
    if (len(courses) == 0):
        return None
    course = courses[0]
    print('course', course)
    course_json = course.to_json()
    return course_json
    return {
        "unique_id": course.unique_id,
        "title": course.title,
        "description": course.description,
        "tags": course.tags,
        "topics": course.topics
    }

def fetch_courses(filter_list=[], relationships_list=[]):
    method_name = "fetch_courses"

    try:
        db_res = course_model_v2().get_details_by_filter_list(filter_list, relationships_list = relationships_list)
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