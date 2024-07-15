import http
import logging
import uuid
from datetime import datetime

from pharma_gyan_proj.common.constants import TAG_FAILURE, TAG_SUCCESS
from pharma_gyan_proj.db_models.chapter_model import chapter_model
from pharma_gyan_proj.orm_models.content.chapter_orm_model import pg_chapter
from pharma_gyan_proj.middlewares.HttpRequestInterceptor import Session
from pharma_gyan_proj.exceptions.failure_exceptions import BadRequestException, InternalServerError
from pharma_gyan_proj.apps.pharma_gyan.app_settings import MAX_ALLOWED_CHAPTER_NAME_LENGTH , \
    MIN_ALLOWED_CHAPTER_NAME_NAME_LENGTH

logger = logging.getLogger("apps")
def prepare_and_save_chapter(request_body):
    method_name = "prepare_and_save_save_chapter"
    logger.debug(f"Entry {method_name}, request_body: {request_body}")

    session = Session()
    validate_chapter_details(request_body)
    try:
        existing_chapter_name = chapter_model().get_chapter_by_title(request_body.get('title'))
        if existing_chapter_name is not None and len(existing_chapter_name) > 0:
            if request_body.get('id') is None or existing_chapter_name[0].unique_id != request_body.get('unique_id'):
                return dict(status_code=http.HTTPStatus.CONFLICT, result=TAG_FAILURE,
                            details_message="Duplicate title found. Please use a different title.")
    except InternalServerError as ey:
        logger.error(f"Error while fetching Chapter by title InternalServerError :: {ey.reason}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                    details_message="Error while fetching Chapter!")
    except Exception as e:
        logger.error(f"Error while fetching Chapter by title :: {e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                    details_message="Error while fetching chapter !")

    if request_body.get('id') is not None:
        filter_list = [{"column": "unique_id", "value": request_body.get('unique_id'), "op": "=="}]
        try:
            chapter = chapter_model().get_details_by_filter_list(filter_list)
            db_resp = chapter_model().get_max_version_by_uid(request_body.get('unique_id'))
            if db_resp is not None and len(db_resp) > 0:
                logger.error(f"{method_name} :: Error while fetching latest version! "
                             f"Error: {db_resp.get('result', None)}")
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
        if chapter is None:
            return dict(status_code=http.HTTPStatus.BAD_REQUEST, result=TAG_FAILURE,
                        details_message="Chapter is not found. Please add Chapter first!")
        chapter = chapter[0]
        chapter.version = db_resp[0].version + 1
    else:
        chapter = pg_chapter()
        chapter.unique_id = uuid.uuid4().hex
        chapter.version = 1
    chapter.title = request_body.get('title')
    chapter.content = request_body.get('content')
    chapter.mark_as_free = request_body.get('is_free')
    chapter.client_id = request_body.get('client_id')
    chapter.created_by = session.admin_user_session.user_name

    try:
        db_res = chapter_model().upsert(chapter)
        if not db_res.get("status"):
            return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                        detailed_message="Unable to save chapter")
        chapter = db_res["response"]
        # prepare_and_save_activity_logs(wa_content)
    except Exception as e:
        logger.error(f"Error while saving or updating Chapter Exception ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                    detailed_message="Error while saving or updating Chapter code!")

    logger.debug(f"Exit {method_name}, Success")
    return dict(status_code=http.HTTPStatus.OK, result=TAG_SUCCESS, data=dict(unique_id=chapter.unique_id))

def validate_chapter_details(request_body):
    method_name = "validate_chapter_details"
    logger.debug(f"Entry {method_name}, request_body: {request_body}")
    # if request_body.get('title') is None:
    title = request_body.get('title')
    if title is None or title.strip() == '':
        raise BadRequestException(method_name=method_name, reason="Chapter name can not be blanked")
    # if request_body.get('content') is None:
    content = request_body.get('content')
    if content is None or content.strip() == '':
        raise BadRequestException(method_name=method_name, reason="Chapter name can not be blanked")
    logger.debug(f"Exit {method_name}, Success")


def fetch_and_prepare_chapter_preview(unique_id):
    method_name = "fetch_and_prepare_chapter_preview"
    logger.debug(f"Entry {method_name}")

    try:
        filter_list = [{"column": "unique_id", "value": unique_id, "op": "=="}]
        chapter = chapter_model().get_details_by_filter_list(filter_list)
    except InternalServerError as ey:
        logger.error(
            f"Error while fetching chapter InternalServerError ::{ey.reason}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    except Exception as e:
        logger.error(f"Error while fetching chapter ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    if chapter is None:
        return dict(status_code=http.HTTPStatus.BAD_REQUEST, result=TAG_FAILURE,
                    details_message="Chapter is not found. Please add chapter first!")
    logger.debug(f"Exit {method_name}")
    chapter = chapter[0]._asdict()
    chapter['ct'] = chapter['ct'].strftime('%d %b %Y, %I:%M %p')
    return chapter

def fetch_and_prepare_chapters():
    method_name = "fetch_and_prepare_chapters"
    logger.debug(f"Entry {method_name}")
    try:
        chapters = chapter_model().get_details_by_filter_list([])
    except InternalServerError as ey:
        logger.error(
            f"Error while fetching users InternalServerError ::{ey.reason}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    except Exception as e:
        logger.error(f"Error while fetching users ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    if chapters is None:
        return dict(status_code=http.HTTPStatus.BAD_REQUEST, result=TAG_FAILURE,
                    details_message="Chapter is not found. Please add chapter first!")

# Convert list of model instances to list of dictionaries
    chapter_list = []
    for chapter in chapters:
        if chapter.is_active:
            cta = "<button id=\"deact-{}\" class=\"btn-outline-danger btn-sm mr-1\" onclick=\"deactivateChapter('{}')\">Deactivate</button>".format(
                chapter.unique_id, chapter.unique_id)
        else:
            cta = "<button id=\"act-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"activateChapter('{}')\">Activate</button>".format(
                chapter.unique_id, chapter.unique_id)
        chapter_list.append({
            "unique_id": chapter.unique_id,
            "title": chapter.title,
            "mark_as_free": chapter.mark_as_free,
            "version": chapter.version,
            "is_active": chapter.is_active,
            "created_by": chapter.created_by,
            "edit": "<button id=\"edit-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"editChapter('{}')\">Edit</button>".format(
                 chapter.unique_id, chapter.unique_id),
            "clone": "<button id=\"clone-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"cloneChapter('{}')\">Clone</button>".format(chapter.unique_id, chapter.unique_id),
            "cta": cta
        })
    return chapter_list

def deactivate_chapter_view(unique_id):
    method_name = "deactivate_chapter_view"
    try:
        filter_list = [{"column": "unique_id", "value": unique_id, "op": "=="}]
        chapter_model().update_by_filter_list(filter_list, dict(is_active=0))
    except Exception as e:
        logger.error(f"Error while deleting chapter ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)

    logger.debug(f"Exit {method_name}, Success")
    return dict(status_code=http.HTTPStatus.OK, result=TAG_SUCCESS)

def activate_chapter_view(unique_id):
    method_name = "activate_chapter_view"

    try:
        filter_list = [{"column": "unique_id", "value": unique_id, "op": "=="}]
        chapter = chapter_model().get_details_by_filter_list(filter_list)
        if chapter is None or len(chapter) < 1:
            return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                        detailed_message="chapter id is incorrect!")
        chapter_model().update_by_filter_list(filter_list, dict(is_active=1))
    except InternalServerError as ey:
        logger.error(
            f"Error while fetching chapter InternalServerError ::{ey.reason}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    except Exception as e:
        logger.error(f"Error while deleting chapter ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)

    logger.debug(f"Exit {method_name}, Success")
    return dict(status_code=http.HTTPStatus.OK, result=TAG_SUCCESS)


def fetch_chapter_by_unique_id(unique_id):
    filter_list = [{"column": "unique_id", "value": unique_id, "op": "=="}]
    try:
        chapter = chapter_model().get_details_by_filter_list(filter_list)
    except InternalServerError as ey:
        logger.error(
            f"Error while fetching chapter InternalServerError ::{ey.reason}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    except Exception as e:
        logger.error(f"Error while fetching chapter ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    if chapter is None:
        return dict(status_code=http.HTTPStatus.BAD_REQUEST, result=TAG_FAILURE,
                    details_message="chapter is not found. Please add chapter first!")
    chapter = chapter[0]
    chapter_dict = {
        "title": chapter.title,
        "content": chapter.content,
        "mark_as_free": chapter.mark_as_free,
        'unique_id': chapter.unique_id,
        'id': chapter.id
    }
    return chapter_dict



