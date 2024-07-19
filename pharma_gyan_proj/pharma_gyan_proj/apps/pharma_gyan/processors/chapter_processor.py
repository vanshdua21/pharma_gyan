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
                        details_message="Promo code is not found. Please add Chapter first!")
        chapter = chapter[0]
        chapter.version = db_resp[0].version + 1
    else:
        chapter = pg_chapter()
        chapter.unique_id = uuid.uuid4().hex
        chapter.version = 1
    chapter.title = request_body.get('title')
    chapter.content = request_body.get('content')
    chapter.mark_as_free = request_body.get('is_free')
    chapter.client_id = '123'
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


def fetch_and_prepare_chapter_view(is_active=False):
    method_name = "fetch_and_prepare_chapter_view"
    logger.debug(f"Entry {method_name}")

    try:
        filter_list = []
        if is_active:
            filter_list.append({"column": "is_active", "value": 1, "op": "=="})
        chapter = chapter_model().get_details_by_filter_list(filter_list)
    except InternalServerError as ey:
        logger.error(
            f"Error while fetching chapter InternalServerError ::{ey.reason}")
        raise InternalServerError(method_name=method_name,
                                  reason="Unable to fetch chapter details")
    except Exception as e:
        logger.error(f"Error while fetching chapter ::{e}")
        raise InternalServerError(method_name=method_name,
                                  reason="Error while fetching chapter!")
    if chapter is None:
        raise BadRequestException(method_name=method_name,
                                  reason="Chapter is not found. Please add chapter first!")
    chapter_list = []
    for chapter_obj in chapter:
        if chapter_obj.is_active:
            cta = "<button id=\"deact-{}\" class=\"btn-outline-danger btn-sm mr-1\" onclick=\"deactivateChapter('{}')\">Deactivate</button>".format(
                chapter_obj.unique_id, chapter_obj.unique_id)
        else:
            cta = "<button id=\"act-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"activateChapter('{}')\">Activate</button>".format(
                chapter_obj.unique_id, chapter_obj.unique_id)
        chapter_list.append(dict(
            id=chapter_obj.id,
            unique_id=chapter_obj.unique_id,
            client_id=chapter_obj.client_id,
            title=chapter_obj.title,
            mark_as_free=chapter_obj.mark_as_free,
            version=chapter_obj.version,
            is_active=chapter_obj.is_active,
            created_by=chapter_obj.created_by,
            ct=chapter_obj.ct.strftime('%d %b %Y, %I:%M %p'),
            add="<button id=\"add-chapter-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"addChapter(('{}'), ('{}'), ('{}'))\">Add</button>".format(chapter_obj.unique_id, chapter_obj.unique_id, chapter_obj.title, chapter_obj.version),
            clone="<button id=\"clone-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"cloneEntityTag('{}')\">Clone</button>".format(
            chapter_obj.unique_id, chapter_obj.unique_id),
            edit="<button id=\"edit-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"editChapter('{}')\">Edit</button>".format(
            chapter_obj.unique_id, chapter_obj.unique_id),
            cta=cta
        ))
    return chapter_list
