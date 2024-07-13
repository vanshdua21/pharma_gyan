import http
import logging
import uuid
from datetime import datetime

from pharma_gyan_proj.apps.pharma_gyan.app_settings import MAX_ALLOWED_ENTITY_NAME_LENGTH, \
    MIN_ALLOWED_ENTITY_NAME_LENGTH, MAX_ALLOWED_DESCRIPTION_LENGTH, MIN_ALLOWED_DESCRIPTION_LENGTH
from pharma_gyan_proj.common.comman import is_valid_alpha_numeric_space_under_score
from pharma_gyan_proj.common.constants import TAG_FAILURE, TAG_SUCCESS
from pharma_gyan_proj.db_models.entity_tag import entity_tag_model
from pharma_gyan_proj.db_models.tag_catagory_model import tag_category_model
from pharma_gyan_proj.exceptions.failure_exceptions import InternalServerError, BadRequestException
from pharma_gyan_proj.middlewares.HttpRequestInterceptor import Session
from pharma_gyan_proj.orm_models.entity_tag_orm_model import pg_entity_tag

logger = logging.getLogger("apps")
def fetch_and_prepare_entity_tag():
    method_name = "fetch_and_prepare_promo_code"
    logger.debug(f"Entry {method_name}")
    try:
        # Fetch all active tag categories
        active_tag_categories = tag_category_model().get_details_by_filter_list(
            [{"column": "is_active", "value": 1, "op": "=="}])

        if active_tag_categories is None:
            return dict(status_code=http.HTTPStatus.BAD_REQUEST, result=TAG_FAILURE,
                        details_message="No active tag categories found!")

        # Create a dictionary for quick lookup of tag_category titles by unique_id
        tag_category_dict = {tag.unique_id: tag.title for tag in active_tag_categories}
        # Fetch all entity tags
        entity_tag = entity_tag_model().get_details_by_filter_list([])
    except InternalServerError as ey:
        logger.error(
            f"Error while fetching users InternalServerError ::{ey.reason}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    except Exception as e:
        logger.error(f"Error while fetching users ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    if entity_tag is None:
        return dict(status_code=http.HTTPStatus.BAD_REQUEST, result=TAG_FAILURE,
                    details_message="Entity tag not found. Please add entity first!")
# Convert list of model instances to list of dictionaries
    entity_tag_list = []
    for entity in entity_tag:

        tag_title = tag_category_dict.get(entity.tag_category_id, "Unknown Tag Category")
        if entity.is_active:
            cta = "<button id=\"deact-{}\" class=\"btn-outline-danger btn-sm mr-1\" onclick=\"deactivateEntityTag('{}')\">Deactivate</button>".format(
                entity.unique_id, entity.unique_id)
        else:
            cta = "<button id=\"act-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"activateEntityTag('{}')\">Activate</button>".format(
                entity.unique_id, entity.unique_id)
        entity_tag_list.append({
            "unique_id": entity.unique_id,
            "title": entity.title,
            "description": entity.description,
            "tag_category": tag_title,
            "created_by": entity.created_by,
            "is_active": entity.is_active,
            "cta": cta,
            "clone": "<button id=\"clone-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"cloneEntityTag('{}')\">Clone</button>",
        })
    return entity_tag_list

def prepare_and_save_entity_tag(request_body):
    method_name = "prepare_and_save_entity_tag"
    logger.debug(f"Entry {method_name}, request_body: {request_body}")

    session = Session()

    validate_entity_tag_details(request_body)

    try:
        existing_entity_tag = entity_tag_model().get_entity_tag_by_title_and_tag_category(request_body.get('title'), request_body.get('tag_category'))
        if existing_entity_tag is not None and len(existing_entity_tag) > 0:
            if request_body.get('id') is None or existing_entity_tag[0].unique_id != request_body.get('unique_id'):
                return dict(status_code=http.HTTPStatus.CONFLICT, result=TAG_FAILURE,
                            details_message="Duplicate entity tag found. Please use a different entity title or different level.")

    except InternalServerError as ey:
        logger.error(f"Error while fetching entity tag by title InternalServerError :: {ey.reason}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                    details_message="Error while fetching entity tag!")
    except Exception as e:
        logger.error(f"Error while fetching entity tag by title :: {e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                    details_message="Error while fetching entity tage !")

    entity_tag = pg_entity_tag()
    entity_tag.unique_id = uuid.uuid4().hex
    entity_tag.client_id = '123'
    entity_tag.title = request_body.get('title')
    entity_tag.description = request_body.get('description')
    entity_tag.tag_category_id = request_body.get('tag_category')
    entity_tag.created_by = session.admin_user_session.user_name

    try:
        db_res = entity_tag_model().upsert(entity_tag)
        if not db_res.get("status"):
            return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                        detailed_message="Unable to save entity tag details!")
    except Exception as e:
        logger.error(f"Error while saving or updating entity tag Exception ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                    detailed_message="Error while saving or updating entity tag!")

    logger.debug(f"Exit {method_name}, Success")
    return dict(status_code=http.HTTPStatus.OK, result=TAG_SUCCESS)


def validate_entity_tag_details(request_body):
    method_name = "validate_entity_tag_details"
    logger.debug(f"Entry {method_name}, request_body: {request_body}")
    tag_category_unique_id = request_body.get('tag_category')

    if not tag_category_unique_id:
        raise BadRequestException(method_name=method_name, reason="Tag category value is missing")
    tag_category_model_instance = tag_category_model()
    tag_category = tag_category_model_instance.get_tag_category_by_unique_id(tag_category_unique_id)
    if not tag_category:
        raise BadRequestException(method_name=method_name, reason="Tag category value is incorrect")

    validate_entity_tag_title(request_body.get('title'))
    validate_entity_tag_desc(request_body.get('description'))

    logger.debug(f"Exit {method_name}, Success")


def validate_entity_tag_title(name):
    method_name = "validate_entity_tag_title"
    logger.debug(f"Entry {method_name}, name: {name}")
    if name is None:
        raise BadRequestException(method_name=method_name, reason="Title is not provided")
    if len(name) > MAX_ALLOWED_ENTITY_NAME_LENGTH  or len(name) < MIN_ALLOWED_ENTITY_NAME_LENGTH :
        raise BadRequestException(method_name=method_name,
                                  reason=F"Title length should be from {MIN_ALLOWED_ENTITY_NAME_LENGTH } to {MAX_ALLOWED_ENTITY_NAME_LENGTH }")

    if is_valid_alpha_numeric_space_under_score(name) is False:
        raise BadRequestException(method_name=method_name,
                                  reason="Title format incorrect, only alphanumeric, space and underscore characters allowed")
    logger.debug(f"Exit {method_name}, Success")


def validate_entity_tag_desc(description):
    method_name = "validate_entity_tag_desc"
    logger.debug(f"Entry {method_name}, Description: {description}")
    if description is None:
        raise BadRequestException(method_name=method_name, reason="Description is not provided")
    if len(description) > MAX_ALLOWED_DESCRIPTION_LENGTH or len(description) < MIN_ALLOWED_DESCRIPTION_LENGTH:
        raise BadRequestException(method_name=method_name,
                                  reason=F"Description length should be from {MIN_ALLOWED_DESCRIPTION_LENGTH} to {MAX_ALLOWED_DESCRIPTION_LENGTH}")
    logger.debug(f"Exit {method_name}, Success")


def deactivate_entity(unique_id):
    method_name = "deactivate_entity"
    try:
        filter_list = [{"column": "unique_id", "value": unique_id, "op": "=="}]
        entity_tag_model().update_by_filter_list(filter_list, dict(is_active=0))
    except Exception as e:
        logger.error(f"Error while deleting user ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)

    logger.debug(f"Exit {method_name}, Success")
    return dict(status_code=http.HTTPStatus.OK, result=TAG_SUCCESS)

def activate_entity(unique_id):
    method_name = "activate_entity"

    try:
        filter_list = [{"column": "unique_id", "value": unique_id, "op": "=="}]
        entity_tag = entity_tag_model().get_details_by_filter_list(filter_list)
        if entity_tag is None or len(entity_tag) < 1:
            return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                        detailed_message="entity tag id is incorrect!")
        entity_tag_model().update_by_filter_list(filter_list, dict(is_active=1))
    except InternalServerError as ey:
        logger.error(
            f"Error while fetching users InternalServerError ::{ey.reason}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    except Exception as e:
        logger.error(f"Error while deleting user ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)

    logger.debug(f"Exit {method_name}, Success")
    return dict(status_code=http.HTTPStatus.OK, result=TAG_SUCCESS)

