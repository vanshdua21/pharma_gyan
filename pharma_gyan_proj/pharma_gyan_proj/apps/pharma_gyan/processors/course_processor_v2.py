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
from pharma_gyan_proj.middlewares.HttpRequestInterceptor import Session

logger = logging.getLogger("apps")


def prepare_and_save_course_v2(request_body):
    method_name = "prepare_and_save_course_v2"
    logger.debug(f"Entry {method_name}, request_body: {request_body}")

    existing_course = get_course_by_title(request_body.get('title'))
    if existing_course is not None and len(existing_course) > 0:
        if existing_course[0].unique_id != request_body.get('unique_id'):
            return dict(status_code=http.HTTPStatus.CONFLICT, result=TAG_FAILURE,
                        details_message="Duplicate title found. Please use a different title.")

    course = Course()
    # if (request_body.get('id')):
    #     course.id = request_body.get('id')
    course.unique_id = uuid.uuid4().hex if request_body.get('unique_id') is None else request_body.get('unique_id')
    session = Session()
    course.client_id = session.admin_user_session.client_id
    course.title = request_body.get('title')
    course.description = request_body.get('description')

    filter_list = [{"column": "unique_id", "value": course.unique_id, "op": "=="}]
    version_count = course_model_v2().fetch_count_by_filter(filter_list)
    course.version = version_count + 1
    
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

def get_course_by_title(title):
        filter_list = [{"column": "title", "value": title, "op": "=="}]
        return course_model_v2().get_details_by_filter_list(filter_list=filter_list)

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
    session = Session()
    client_id = session.admin_user_session.client_id
    filter_list = [{"column": "client_id", "value": client_id, "op": "=="}]
    courses = fetch_courses(filter_list)
    courses_list = []
    for course in courses:
        tag_ids = [tag.tag_id for tag in course.tags]
        filter_list = [{"column": "unique_id", "value": tag_ids, "op": "IN"}]
        tags = entity_tag_model().get_details_by_filter_list(filter_list=filter_list)
        editBtn = "<button id=\"edit-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"editCourse('{}')\">Edit</button>".format(course.id, course.id)
        if course.is_active:
            cta = "<button id=\"deact-{}\" class=\"btn-outline-danger btn-sm mr-1\" onclick=\"deactivateCourse('{}')\">Deactivate</button>".format(
                course.id, course.id)
        else:
            cta = "<button id=\"act-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"activateCourse('{}')\">Activate</button>".format(
                course.id, course.id)
        courses_list.append({
            "id": course.id,
            "unique_id": course.unique_id,
            "title": course.title,
            "description": course.description,
            "tags": [tag.title for tag in tags] if tags is not None else [],
            "topics_count": len(course.topics),
            "is_active": course.is_active,
            "clone": "<button id=\"clone-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"cloneCourse('{}')\">Clone</button>".format(
                course.id, course.id),
            "edit": editBtn,
            "cta": cta,
            # "is_active": user.is_active,
            # "edit": "<button id=\"edit-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"editUser('{}')\">Edit</button>".format(user.unique_id, user.unique_id),
            # "del": "<button id=\"del-{}\" class=\"btn-outline-danger btn-sm mr-1\" onclick=\"delUser('{}')\">Delete</button>".format(user.unique_id, user.unique_id)
        })
    return courses_list

def fetch_course_from_id_v2(course_id):
    print('fetch_course_from_id_v2, course_id', course_id)
    session = Session()
    client_id = session.admin_user_session.client_id
    filter_list = [{"column": "id", "value": course_id, "op": "=="}, {"column": "client_id", "value": client_id, "op": "=="}]
    courses = fetch_courses(filter_list)
    print('length', len(courses))
    if (len(courses) == 0):
        return None
    course = courses[0]
    print('course', course)
    course_json = course.to_json()
    return course_json

def fetch_all_courses(filter_list=[], relationships_list=[]):
    method_name = "fetch_all_courses"
    logger.debug(f"Entry {method_name}")
    session = Session()
    client_id = session.admin_user_session.client_id
    filter_list = [{"column": "client_id", "value": client_id, "op": "=="}]
    courses = fetch_courses(filter_list)
    courses_list = []
    for course in courses:
        courses_list.append({
            "id": course.id,
            "unique_id": course.unique_id,
            "title": course.title,
            "topics_count": len(course.topics),
            "add": "<button id=\"add-course-{}\" class='btn-outline-success btn-sm mr-1' onclick=\"addCourse('{}', '{}', '{}')\">Add</button>".format(course.unique_id, course.unique_id, course.title, len(course.topics))
        })
    return courses_list

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

def process_deactivate_course_v2(course_id):
    method_name = "process_deactivate_course_v2"

    try:
        session = Session()
        client_id = session.admin_user_session.client_id
        filter_list = [{"column": "id", "value": course_id, "op": "=="}, {"column": "client_id", "value": client_id, "op": "=="}]
        course_model_v2().update_by_filter_list(filter_list, dict(is_active=0))
    except Exception as e:
        logger.error(f"Error while deactivating course ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)

    logger.debug(f"Exit {method_name}, Success")
    return dict(status_code=http.HTTPStatus.OK, result=TAG_SUCCESS)


def process_activate_course_v2(course_id):
    method_name = "process_activate_course_v2"

    try:
        session = Session()
        client_id = session.admin_user_session.client_id
        filter_list = [{"column": "id", "value": course_id, "op": "=="}, {"column": "client_id", "value": client_id, "op": "=="}]
        course_model_v2().update_by_filter_list(filter_list, dict(is_active=1))
    except InternalServerError as ey:
        logger.error(
            f"Error while fetching courses InternalServerError ::{ey.reason}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    except Exception as e:
        logger.error(f"Error while deleting user ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)

    logger.debug(f"Exit {method_name}, Success")
    return dict(status_code=http.HTTPStatus.OK, result=TAG_SUCCESS)