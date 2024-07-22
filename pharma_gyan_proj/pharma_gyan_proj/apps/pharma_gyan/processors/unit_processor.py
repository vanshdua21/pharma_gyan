import http
import json
import logging
from urllib.parse import unquote_plus
import uuid
from datetime import datetime
from django.core.files.storage import FileSystemStorage

from pharma_gyan_proj.apps.pharma_gyan.app_settings import MAX_ALLOWED_TOPIC_NAME_LENGTH, MIN_ALLOWED_TOPIC_NAME_LENGTH, \
    MIN_ALLOWED_DESCRIPTION_LENGTH, MAX_ALLOWED_DESCRIPTION_LENGTH
from pharma_gyan_proj.common.comman import is_valid_alpha_numeric_space_under_score, get_latest_id_list_of_dict
from pharma_gyan_proj.common.constants import TAG_FAILURE, TAG_SUCCESS, AdminUserPermissionType, ACTIVE_CHAPTER_CHECK
from pharma_gyan_proj.db_models.chapter_model import chapter_model
from pharma_gyan_proj.db_models.topic_chapter_mapping_model import topic_chapter_mapping_model
from pharma_gyan_proj.db_models.topic_model import topic_model
from pharma_gyan_proj.exceptions.failure_exceptions import BadRequestException, InternalServerError
from pharma_gyan_proj.middlewares.HttpRequestInterceptor import Session
from pharma_gyan_proj.orm_models.content.chapter_orm_model import pg_chapter
from pharma_gyan_proj.orm_models.content_models import PgCourse, PgSemester, PgSubject, PgTopic, PgChapter
from pharma_gyan_proj.orm_models.topic_chapter_mapping_orm_model import pg_topic_chapter_mapping
from pharma_gyan_proj.orm_models.topic_orm_model import pg_topic

logger = logging.getLogger("apps")

def prepare_and_save_unit(request_body):
    method_name = "prepare_and_save_unit"
    logger.debug(f"Entry {method_name}, request_body: {request_body}")

    unit = PgTopic()
    if (request_body.get('id')):
        unit.id = request_body.get('id')
    unit.unique_id = uuid.uuid4().hex if request_body.get('unique_id') is None else request_body.get('unique_id')
    unit.title = request_body.get('title')
    if (request_body.get('ct')):
        unit.ct = request_body.get('ct')
        
    unit.chapters = []
    chaptersBody = request_body.get('chapters')
    if chaptersBody:
        for chap in chaptersBody:
            chapter = PgChapter()
            chapter.id = chap.get('id')
            chapter.unique_id = uuid.uuid4().hex
            chapter.title = chap.get('title')
            chapter.content = chap.get('content')
            chapter.index = chap.get('index')
            chapter.mark_as_free = chap.get('mark_as_free')
            unit.chapters.append(chapter)
    
    try:
        print('unit debug',unit)
        save_or_update_unit(unit)
    except Exception as e:
        logger.error(f"Error while saving or updating unit ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    
    logger.debug(f"Exit {method_name}, Success")
    return dict(status_code=http.HTTPStatus.OK, result=TAG_SUCCESS)


def prepare_and_save_topic(request_body):
    method_name = "prepare_and_save_topic"
    logger.debug(f"Entry {method_name}, request_body: {request_body}")

    session = Session()

    validate_topic_details(request_body)
    try:
        existing_topic_name = topic_model().get_topic_by_title(request_body.get('title'))
        if existing_topic_name is not None and len(existing_topic_name) > 0:
            if request_body.get('id') is None or existing_topic_name[0].unique_id != request_body.get('unique_id'):
                return dict(status_code=http.HTTPStatus.CONFLICT, result=TAG_FAILURE,
                            details_message="Duplicate title found. Please use a different title.")
    except InternalServerError as ey:
        logger.error(f"Error while fetching topic by title InternalServerError :: {ey.reason}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                    details_message="Error while fetching Topic!")
    except Exception as e:
        logger.error(f"Error while fetching topic by title :: {e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                    details_message="Error while fetching Topic !")
    if request_body.get('id') is not None:
        filter_list = [{"column": "unique_id", "value": request_body.get('unique_id'), "op": "=="}]
        try:
            topic_db_obj = topic_model().get_details_by_filter_list(filter_list)
            db_resp = topic_model().get_max_version_by_uid(request_body.get('unique_id'))
            if db_resp is not None and len(db_resp) < 0:
                logger.error(f"{method_name} :: Error while fetching latest version!")
                return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                            details_message="While fetching latest version!")
        except InternalServerError as ey:
            logger.error(
                f"Error while fetching users InternalServerError ::{ey.reason}")
            return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                        details_message="Something went wrong!")
        except Exception as e:
            logger.error(f"Error while fetching users ::{e}")
            return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                        details_message="Something went wrong !")
        if topic_db_obj is None:
            return dict(status_code=http.HTTPStatus.BAD_REQUEST, result=TAG_FAILURE,
                        details_message="Topic is not found. Please add topic first!")

        topic_db_obj = topic_db_obj[0]
        topic = pg_topic()
        version = db_resp[0].get('version') + 1
        unique_id = topic_db_obj.unique_id
        topic.version = version
        topic.ct = topic_db_obj.ct
        topic.unique_id = topic_db_obj.unique_id
        topic.id = None
    else:
        version = 1
        unique_id = uuid.uuid4().hex
        topic = pg_topic()
        topic.unique_id = unique_id
        topic.version = version
    topic.title = request_body.get('title')
    topic.description = request_body.get('description')
    topic.client_id = request_body.get('client_id')
    topic.created_by = session.admin_user_session.user_name

    try:
        db_res = topic_model().upsert(topic)
        if not db_res.get("status"):
            return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                        detailed_message="Unable to save topic details!")
        prepare_and_save_chapter_mapping(request_body.get('chapters'), unique_id, version)
    except Exception as e:
        logger.error(f"Error while saving or updating topic Exception ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                    detailed_message="Error while saving or updating topic!")

    logger.debug(f"Exit {method_name}, Success")
    return dict(status_code=http.HTTPStatus.OK, result=TAG_SUCCESS)


def process_activate_topic(unique_id, version):
    method_name = "process_activate_topic"

    try:
        filter_list = [{"column": "unique_id", "value": unique_id, "op": "=="},
                       {"column": "version", "value": version, "op": "=="}]
        course = topic_model().get_details_by_filter_list(filter_list)
        if course is None or len(course) < 1:
            return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                        detailed_message="Topic id is incorrect!")
        topic_model().update_by_filter_list(filter_list, dict(is_active=1))
    except InternalServerError as ey:
        logger.error(
            f"Error while fetching topic InternalServerError ::{ey.reason}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    except Exception as e:
        logger.error(f"Error while fetching topic ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)

    logger.debug(f"Exit {method_name}, Success")
    return dict(status_code=http.HTTPStatus.OK, result=TAG_SUCCESS)


def process_deactivate_topic(unique_id, version):
    method_name = "process_deactivate_topic"

    try:
        filter_list = [{"column": "unique_id", "value": unique_id, "op": "=="},
                       {"column": "version", "value": version, "op": "=="}]
        course = topic_model().get_details_by_filter_list(filter_list)
        if course is None or len(course) < 1:
            return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                        detailed_message="Topic id is incorrect!")
        topic_model().update_by_filter_list(filter_list, dict(is_active=0))
    except InternalServerError as ey:
        logger.error(
            f"Error while fetching topic InternalServerError ::{ey.reason}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    except Exception as e:
        logger.error(f"Error while fetching topic ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)

    logger.debug(f"Exit {method_name}, Success")
    return dict(status_code=http.HTTPStatus.OK, result=TAG_SUCCESS)

def fetch_and_prepare_topic():
    method_name = "fetch_and_prepare_topic"
    logger.debug(f"Entry {method_name}")
    session = Session()
    client_id = session.admin_user_session.client_id
    try:
        # Fetch all entity tags
        topic = topic_model().get_details_by_filter_list([{"column": "client_id", "value": client_id, "op": "=="}])
    except InternalServerError as ey:
        logger.error(
            f"Error while fetching topic InternalServerError ::{ey.reason}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    except Exception as e:
        logger.error(f"Error while fetching topic ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    if topic is None:
        return dict(status_code=http.HTTPStatus.BAD_REQUEST, result=TAG_FAILURE,
                    details_message="Topic not found. Please add topic first!")

    topic = get_latest_id_list_of_dict(topic)

    # Convert list of model instances to list of dictionaries
    topic_list = []
    for topic_obj in topic:
        if topic_obj.is_active:
            cta = "<button id=\"deact-{}\" class=\"btn-outline-danger btn-sm mr-1\" onclick=\"deactivateTopic('{}', '{}')\">Deactivate</button>".format(
                topic_obj.unique_id, topic_obj.unique_id, topic_obj.version)
        else:
            cta = "<button id=\"act-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"activateTopic('{}', '{}')\">Activate</button>".format(
                topic_obj.unique_id, topic_obj.unique_id, topic_obj.version)
        topic_list.append({
            "id": topic_obj.id,
            "unique_id": topic_obj.unique_id,
            "title": topic_obj.title,
            "description": topic_obj.description,
            "created_by": topic_obj.created_by,
            "is_active": topic_obj.is_active,
            "cta": cta,
            "version": topic_obj.version,
            "add": "<button id=\"add-topic-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"addTopic(('{}'), ('{}'), ('{}'))\">Add</button>".format(topic_obj.unique_id, topic_obj.unique_id, topic_obj.title, topic_obj.version),
            "clone": "<button id=\"clone-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"cloneTopic('{}', '{}')\">Clone</button>".format(
                topic_obj.unique_id, topic_obj.unique_id, topic_obj.version),
            "edit": "<button id=\"edit-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"editTopic('{}', '{}')\">Edit</button>".format(
                topic_obj.unique_id, topic_obj.unique_id, topic_obj.version),
        })
    return topic_list



def fetch_topic_by_unique_id(unique_id, version):
    filter_list = [{"column": "unique_id", "value": unique_id, "op": "=="},
                   {"column": "version", "value": version, "op": "=="}]
    try:
        topic = topic_model().get_details_by_filter_list(filter_list)
    except InternalServerError as ey:
        logger.error(
            f"Error while fetching topic InternalServerError ::{ey.reason}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    except Exception as e:
        logger.error(f"Error while fetching topic ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    if topic is None:
        return dict(status_code=http.HTTPStatus.BAD_REQUEST, result=TAG_FAILURE,
                    details_message="Topic is not found. Please add entity tag first!")
    topic = topic[0]
    # Fetch tag categories
    filter_list = [{"column": "topic_id", "value": topic.unique_id, "op": "=="},
                   {"column": "topic_version", "value": topic.version, "op": "=="}]
    topic_chapter_mapping = topic_chapter_mapping_model().get_details_by_filter_list(filter_list)

    if topic_chapter_mapping is None:
        return dict(status_code=http.HTTPStatus.BAD_REQUEST, result=TAG_FAILURE,
                    details_message="Unable to fetch topic associated chapters!")
    chapters = []
    sorted_topic_chapter_mapping = sorted(topic_chapter_mapping, key=lambda x: x.order)
    for chap in sorted_topic_chapter_mapping:
        chapters.append(f"{chap.chapter_id}-version-{chap.chap_version}")
    entity_tag_dict = {
        "id": topic.id,
        "unique_id": topic.unique_id,
        "title": topic.title,
        "description": topic.description,
        "chapters": chapters
    }
    return entity_tag_dict


def prepare_and_save_chapter_mapping(chapters, unique_id, version):
    topic_chapter_mapping = []
    order = 1
    try:
        for chap in chapters:
            [chapter_id, chap_version] = chap.split('-version-')
            mapping = pg_topic_chapter_mapping()
            mapping.unique_id = uuid.uuid4().hex
            mapping.chap_version = chap_version
            mapping.topic_version = version
            mapping.chapter_id = chapter_id
            mapping.topic_id = unique_id
            mapping.order = order
            topic_chapter_mapping.append(mapping)
            order += order
        db_res = topic_chapter_mapping_model().bulk_save_mapping(topic_chapter_mapping)
        if not db_res.get("status"):
            return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                        detailed_message="Unable to save topic chapter mapping!")
    except Exception as e:
        logger.error(f"Error while saving topic chapter mapping Exception ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                    detailed_message="Error while preparing or saving topic chapter mapping!")


def validate_topic_details(request_body):
    method_name = "validate_topic_details"
    logger.debug(f"Entry {method_name}, request_body: {request_body}")

    validate_topic_title(request_body.get('title'))
    validate_topic_description(request_body.get('description'))
    # validate_topic_chapter_mapping(request_body.get('chapters', []), ACTIVE_CHAPTER_CHECK)

    logger.debug(f"Exit {method_name}, Success")


def validate_topic_chapter_mapping(chapters, is_active=False):
    method_name = "validate_topic_chapter_mapping"
    logger.debug(f"Entry {method_name}, chapters: {chapters}")
    if len(chapters) < 1:
        raise BadRequestException(method_name=method_name,
                                  reason=F"Must add At least one chapter!")
    chap_id_list = []
    for chap in chapters:
        [chapter_id, version] = chap.split('-version-')
        chap_id_list.append(chapter_id)
    filter_list = [{"column": "unique_id", "value": chap_id_list, "op": "in"}]
    if is_active:
        filter_list.append({"column": "is_active", "value": 1, "op": "=="})
    chapters_obj_list = chapter_model().get_details_by_filter_list(filter_list)

    if len(chapters) != len(chapters_obj_list):
        raise BadRequestException(method_name=method_name,
                                  reason=F"Invalid chapters!")

    logger.debug(f"Exit {method_name}, Success")

def validate_topic_description(description):
    method_name = "validate_topic_description"
    logger.debug(f"Entry {method_name}, description: {description}")
    if description is None:
        return
    if len(description) > MAX_ALLOWED_DESCRIPTION_LENGTH or len(description) < MIN_ALLOWED_DESCRIPTION_LENGTH:
        raise BadRequestException(method_name=method_name,
                                  reason=F"Description length should be from {MIN_ALLOWED_DESCRIPTION_LENGTH} to {MAX_ALLOWED_DESCRIPTION_LENGTH}")

    logger.debug(f"Exit {method_name}, Success")


def validate_topic_title(name):
    method_name = "validate_topic_title"
    logger.debug(f"Entry {method_name}, name: {name}")
    if name is None:
        raise BadRequestException(method_name=method_name, reason="Title is not provided")
    if len(name) > MAX_ALLOWED_TOPIC_NAME_LENGTH or len(name) < MIN_ALLOWED_TOPIC_NAME_LENGTH:
        raise BadRequestException(method_name=method_name,
                                  reason=F"Title length should be from {MIN_ALLOWED_TOPIC_NAME_LENGTH} to {MAX_ALLOWED_TOPIC_NAME_LENGTH}")

    if is_valid_alpha_numeric_space_under_score(name) is False:
        raise BadRequestException(method_name=method_name,
                                  reason="Title format incorrect, only alphanumeric, space and underscore characters allowed")
    logger.debug(f"Exit {method_name}, Success")

def save_or_update_unit(unit):
    method_name = "save_or_update_course"

    db_res = chapter_model().upsert(unit)
    if not db_res.get("status"):
        raise InternalServerError(method_name=method_name,
                                    reason=db_res.get("response"))

    logger.debug(f"Exit {method_name}, Success")

def fetch_units(filter_list=[], relationships_list=[]):
    method_name = "fetch_units"

    try:
        db_res = chapter_model().get_details_by_filter_list(filter_list, relationships_list = relationships_list)
    except InternalServerError as ey:
        logger.error(
            f"Error while fetching unit InternalServerError ::{ey.reason}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    except Exception as e:
        logger.error(f"Error while unit courses ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)

    logger.debug(f"Exit {method_name}, Success")
    return db_res


def fetch_unit_from_id(unit_id):
    filter_list = [{"column": "unique_id", "value": unit_id, "op": "=="}]
    relationships_list = ["chapters"]
    units = fetch_units(filter_list, relationships_list)
    if (len(units) == 0):
        return None
    unit = units[0]
    unit.chapters = sorted(unit.chapters, key=lambda chapter: chapter.index)
    # Convert list of model instances to list of dictionaries
    unit_json = unit.to_json()
    print(unit_json)
    return unit_json