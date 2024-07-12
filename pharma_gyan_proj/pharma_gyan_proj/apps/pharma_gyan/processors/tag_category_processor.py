import http

from pharma_gyan_proj.common.constants import TAG_FAILURE
from pharma_gyan_proj.db_models.tag_catagory_model import tag_category_model
from pharma_gyan_proj.exceptions.failure_exceptions import InternalServerError
from pharma_gyan_proj.middlewares.HttpRequestInterceptor import logger


def fetch_and_prepare_tag_category():
    method_name = "fetch_and_prepare_tag_catagory"
    logger.debug(f"Entry {method_name}")

    try:
       tag_category = tag_category_model().get_details_by_filter_list([])
    except InternalServerError as ey:
        logger.error(
            f"Error while fetching users InternalServerError ::{ey.reason}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    except Exception as e:
        logger.error(f"Error while fetching users ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    if tag_category is None:
        return dict(status_code=http.HTTPStatus.BAD_REQUEST, result=TAG_FAILURE,
                    details_message="tag category is not found. Please add tag category first!")
    # Convert list of model instances to list of dictionaries
    tag_category_list = []
    for tag in tag_category:
        tag_category_list.append({
            "unique_id": tag.unique_id,
            "title": tag.title,
            "extra": tag.extra,
            "is_active": tag.is_active
        })
    return tag_category_list