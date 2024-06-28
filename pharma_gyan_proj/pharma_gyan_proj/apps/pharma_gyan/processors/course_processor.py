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
    if (request_body.get('id')):
        course.id = request_body.get('id')
    course.unique_id = uuid.uuid4().hex if request_body.get('unique_id') is None else request_body.get('unique_id')
    course.title = request_body.get('title')
    course.description = request_body.get('description')
    course.price = request_body.get('price')
    course.thumbnail_url = request_body.get('imageUrl')
    if (request_body.get('ct')):
        course.ct = request_body.get('ct')
        
    course.semesters = []
    semestersBody = request_body.get('semesters')
    if semestersBody:
        for sem in semestersBody:
            semester = PgSemester()
            if (sem.get('id')):
                semester.id = sem.get('id')
            semester.unique_id = uuid.uuid4().hex if sem.get('unique_id') is None else sem.get('unique_id')
            semester.title = sem.get('semesterId')
            
            semester.subjects = []
            subjectBody = sem.get('subjects')
            if subjectBody:
                for sub in subjectBody:
                    subject = PgSubject()
                    if (sub.get('id')):
                        subject.id = sub.get('id')
                    subject.unique_id = uuid.uuid4().hex if sub.get('unique_id') is None else sub.get('unique_id')
                    subject.name = sub.get('title')
                    subject.description = sub.get('description')
                    
                    subject.units = []
                    unitBody = sub.get('topics')
                    if unitBody:
                        for topic in unitBody:
                            unit = PgUnit()
                            if (topic.get('id')):
                                unit.id = topic.get('id')
                            unit.unique_id = uuid.uuid4().hex if topic.get('unique_id') is None else topic.get('unique_id')
                            unit.title = topic.get('title')
                            
                            subject.units.append(unit)
                    
                    semester.subjects.append(subject)
                
            course.semesters.append(semester)
    
    try: 
        save_or_update_course(course)
    except Exception as e:
        logger.error(f"Error while saving or updating course ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    
    logger.debug(f"Exit {method_name}, Success")
    return dict(status_code=http.HTTPStatus.OK, result=TAG_SUCCESS)

def save_or_update_course(course):
    method_name = "save_or_update_course"

    db_res = course_model().upsert(course)
    if not db_res.get("status"):
        raise InternalServerError(method_name=method_name,
                                    reason=db_res.get("response"))

    logger.debug(f"Exit {method_name}, Success")

def fetch_and_prepare_courses():
    method_name = "fetch_and_prepare_courses"
    logger.debug(f"Entry {method_name}")
    courses = fetch_courses()
    # Convert list of model instances to list of dictionaries
    courses_list = []
    for course in courses:
        editBtn = "<button id=\"edit-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"editCourse('{}')\">Edit</button>".format(course.unique_id, course.unique_id)
        treeBtn = "<button id=\"tree-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"openTreeModal('{}')\">Show Course Structure</button>".format(course.unique_id, course.unique_id)
        if course.is_active:
            deac = "<button id=\"deact-{}\" class=\"btn-outline-danger btn-sm mr-1\" onclick=\"deactivateCourse('{}')\">Deactivate</button>".format(
                course.unique_id, course.unique_id)
        else:
            deac = "<button id=\"act-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"activateCourse('{}')\">Activate</button>".format(
                course.unique_id, course.unique_id)
        courses_list.append({
            "unique_id": course.unique_id,
            "title": course.title,
            "description": course.description,
            "price": str(course.price),
            "image_url": course.thumbnail_url,
            "is_active": course.is_active,
            "tree": treeBtn,
            "edit": editBtn, 
            "deac": deac,
            # "is_active": user.is_active,
            # "edit": "<button id=\"edit-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"editUser('{}')\">Edit</button>".format(user.unique_id, user.unique_id),
            # "del": "<button id=\"del-{}\" class=\"btn-outline-danger btn-sm mr-1\" onclick=\"delUser('{}')\">Delete</button>".format(user.unique_id, user.unique_id)
        })
    return courses_list

def fetch_courses(filter_list=[], relationships_list=[]):
    method_name = "fetch_courses"

    try:
        db_res = course_model().get_details_by_filter_list(filter_list, relationships_list = relationships_list)
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

def fetch_course_from_id(course_id):
    filter_list = [{"column": "unique_id", "value": course_id, "op": "=="}]
    relationships_list = ["semesters", "semesters.subjects", "semesters.subjects.units", "semesters.subjects.units.chapters"]
    courses = fetch_courses(filter_list, relationships_list)
    if (len(courses) == 0):
        return None
    course = courses[0]
    # Convert list of model instances to list of dictionaries
    course_json = course.to_json()
    return course_json

def fetch_course_tree_from_id(course_id):
    filter_list = [{"column": "unique_id", "value": course_id, "op": "=="}]
    relationships_list = ["semesters", "semesters.subjects", "semesters.subjects.units"]
    courses = fetch_courses(filter_list, relationships_list)
    if (len(courses) == 0):
        return None
    course = courses[0]
    course_json = course_to_json(course)
    return dict(status_code=http.HTTPStatus.OK, result=TAG_SUCCESS, data=course_json)

def course_to_json(course):
    def semester_to_dict(semester):
        return {
            "label": 'Semester ' + semester.title,
            "ul": [subject_to_dict(subject) for subject in semester.subjects]
        }

    def subject_to_dict(subject):
        return {
            "label": subject.name,
            "ul": [{"label": unit.title} for unit in subject.units]
        }

    course_dict = [{
        "label": course.title,
        "ul": [semester_to_dict(semester) for semester in course.semesters]
    }]

    return course_dict

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