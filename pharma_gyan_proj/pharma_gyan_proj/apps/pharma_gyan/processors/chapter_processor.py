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
    method_name = "prepare_and_save_chapter"
    logger.debug(f"Entry {method_name}, request_body: {request_body}")

    session = Session()
    validate_chapter_details(request_body)

    # Check for duplicate title
    try:
        existing_chapter = chapter_model().get_chapter_by_title(request_body.get('title'))
        if existing_chapter is not None and len(existing_chapter) > 0:
            if request_body.get('id') is None or existing_chapter[0].unique_id != request_body.get('unique_id'):
                return dict(status_code=http.HTTPStatus.CONFLICT, result=TAG_FAILURE,
                            details_message="Duplicate title found. Please use a different title.")
    except InternalServerError as ey:
        logger.error(f"Error while fetching Chapter by title InternalServerError :: {ey.reason}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                    details_message="Error while fetching Chapter!")
    except Exception as e:
        logger.error(f"Error while fetching Chapter by title :: {e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                    details_message="Error while fetching chapter!")

    # Handling chapter creation or edit
    if request_body.get('id') is not None:
        filter_list = [{"column": "unique_id", "value": request_body.get('unique_id'), "op": "=="}]
        try:
            # Fetch existing chapter details
            existing_chapters = chapter_model().get_details_by_filter_list(filter_list)
            if existing_chapters is None or len(existing_chapters) == 0:
                return dict(status_code=http.HTTPStatus.BAD_REQUEST, result=TAG_FAILURE,
                            details_message="Chapter not found. Please add Chapter first!")

            # Get the maximum version of the existing chapters with the same unique_id
            db_resp = chapter_model().get_max_version_by_uid(request_body.get('unique_id'))
            if db_resp is not None and len(db_resp) > 0 and db_resp[0]['version'] is not None:
                chapter_version = db_resp[0]['version'] + 1
            else:
                chapter_version = 1

            # Create a new chapter entry with the same unique_id but a different id
            chapter = pg_chapter()
            chapter.unique_id = request_body.get('unique_id')
            chapter.version = chapter_version

            # Set all existing chapters with the same unique_id to inactive
            for existing_chapter in existing_chapters:
                existing_chapter.is_active = 0
                chapter_model().upsert(existing_chapter)  # Assuming upsert can handle updates

        except InternalServerError as ey:
            logger.error(f"Error while fetching chapter InternalServerError :: {ey.reason}")
            return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                        details_message="Something went wrong!")
        except Exception as e:
            logger.error(f"Error while fetching chapter :: {e}")
            return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                        details_message="Something went wrong!")
    else:
        # Create a new chapter
        chapter = pg_chapter()
        chapter.unique_id = uuid.uuid4().hex
        chapter.version = 1

    # Set chapter properties
    chapter.title = request_body.get('title')
    chapter.content = request_body.get('content')
    chapter.mark_as_free = request_body.get('is_free')
    chapter.client_id = request_body.get('client_id')
    chapter.created_by = session.admin_user_session.user_name
    chapter.is_active = 1  # Set the new chapter as active

    # Save the chapter
    try:
        db_res = chapter_model().upsert(chapter)
        if not db_res.get("status"):
            return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                        detailed_message="Unable to save chapter")
        chapter = db_res["response"]
    except Exception as e:
        logger.error(f"Error while saving or updating Chapter Exception :: {e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                    detailed_message="Error while saving or updating Chapter code!")

    logger.debug(f"Exit {method_name}, Success")
    return dict(status_code=http.HTTPStatus.OK, result=TAG_SUCCESS, data=dict(unique_id=chapter.unique_id, id=chapter.id))




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

def fetch_and_prepare_chapter_preview_by_id(id):
    method_name = "fetch_and_prepare_chapter_preview"
    logger.debug(f"Entry {method_name}")

    try:
        filter_list = [{"column": "id", "value": id, "op": "=="}]
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
    session = Session()
    client_id = session.admin_user_session.client_id
    try:
        filter_list = [{"column": "client_id", "value": client_id, "op": "=="}]
        chapters = chapter_model().get_details_by_filter_list(filter_list)
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
    chapters = get_latest_id_list_of_dict(chapters)
# Convert list of model instances to list of dictionaries
    chapter_list = []
    for chapter in chapters:
        if chapter.is_active:
            cta = "<button id=\"deact-{}\" class=\"btn-outline-danger btn-sm mr-1\" onclick=\"deactivateChapter('{}')\">Deactivate</button>".format(
                chapter.id, chapter.id)
        else:
            cta = "<button id=\"act-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"activateChapter('{}')\">Activate</button>".format(
                chapter.id, chapter.id)
        chapter_list.append({
            "id": chapter.id,
            "unique_id": chapter.unique_id,
            "title": chapter.title,
            "mark_as_free": chapter.mark_as_free,
            "version": chapter.version,
            "is_active": chapter.is_active,
            "created_by": chapter.created_by,
            "edit": "<button id=\"edit-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"editChapter('{}')\">Edit</button>".format(
                 chapter.id, chapter.id),
            "clone": "<button id=\"clone-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"cloneChapter('{}')\">Clone</button>".format(chapter.id, chapter.id),
            "cta": cta
        })
    return chapter_list

def get_latest_id_list_of_dict(list_of_dict):
    # Dictionary to store the maximum id for each unique_id
    max_id_dict = {}

    # Iterate through the list of dictionaries
    for d in list_of_dict:
        unique_id = d.unique_id
        id_value = d.id

        # If unique_id is not in the dictionary or current id is greater than the stored id
        if unique_id not in max_id_dict or id_value > max_id_dict[unique_id].id:
            max_id_dict[unique_id] = d

    # Extract the dictionaries with the maximum id for each unique_id
    result = list(max_id_dict.values())

    # Print the result
    return result
def deactivate_chapter_view(id):
    method_name = "deactivate_chapter_view"
    try:
        # filter_list = [{"column": "unique_id", "value": unique_id, "op": "=="}]
        filter_list = [{"column": "id", "value": id, "op": "=="}]
        chapter_model().update_by_filter_list(filter_list, dict(is_active=0))
    except Exception as e:
        logger.error(f"Error while deleting chapter ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)

    logger.debug(f"Exit {method_name}, Success")
    return dict(status_code=http.HTTPStatus.OK, result=TAG_SUCCESS)


def activate_chapter_view(id):
    method_name = "activate_chapter_view"

    try:
        # Fetch the chapter with the given id
        filter_list = [{"column": "id", "value": id, "op": "=="}]
        chapter = chapter_model().get_details_by_filter_list(filter_list)
        if chapter is None or len(chapter) < 1:
            return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                        detailed_message="chapter id is incorrect!")

        # Extract the unique_id of the fetched chapter
        unique_id = chapter[0].unique_id
        print(unique_id)
        # Deactivate all entries with the same unique_id
        deactivation_filter_list = [{"column": "unique_id", "value": unique_id, "op": "=="}]
        chapter_model().update_by_filter_list(deactivation_filter_list, dict(is_active=0))

        # Activate the specific chapter
        chapter_model().update_by_filter_list(filter_list, dict(is_active=1))

    except InternalServerError as ey:
        logger.error(
            f"Error while fetching chapter InternalServerError ::{ey.reason}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    except Exception as e:
        logger.error(f"Error while activating chapter ::{e}")
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

def fetch_chapter_by_id(id):
    filter_list = [{"column": "id", "value": id, "op": "=="}]
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

