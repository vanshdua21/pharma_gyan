import http
import logging
import uuid
from datetime import datetime

from pharma_gyan_proj.apps.pharma_gyan.app_settings import MAX_ALLOWED_PROMO_CODE_NAME_LENGTH, \
    MIN_ALLOWED_PROMO_CODE_LENGTH, MAX_ALLOWED_PROMO_CODE_LENGTH, MIN_ALLOWED_PROMO_CODE_NAME_LENGTH
from pharma_gyan_proj.common.comman import is_valid_alpha_numeric_space_under_score
from pharma_gyan_proj.common.constants import TAG_FAILURE, TAG_SUCCESS, PromoCodeDiscountType
from pharma_gyan_proj.db_models.promo_code_model import promo_code_model
from pharma_gyan_proj.middlewares.HttpRequestInterceptor import Session
from pharma_gyan_proj.orm_models.promo_code_orm_model import pg_promo_code
from pharma_gyan_proj.exceptions.failure_exceptions import BadRequestException, InternalServerError
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger("apps")


def prepare_and_save_promo_code(request_body):
    method_name = "prepare_and_save_promo_code"
    logger.debug(f"Entry {method_name}, request_body: {request_body}")

    session = Session()

    validate_promo_code_details(request_body)
    try:
        existing_promo_code = promo_code_model().get_promo_code_by_title_or_pc(request_body.get('title'), request_body.get('promo_code'))
        if existing_promo_code is not None and len(existing_promo_code) > 0:
            if request_body.get('id') is None or existing_promo_code[0].unique_id != request_body.get('unique_id'):
                return dict(status_code=http.HTTPStatus.CONFLICT, result=TAG_FAILURE,
                            details_message="Duplicate promo code found. Please use a different promo code title or promo code value.")
    except InternalServerError as ey:
        logger.error(f"Error while fetching promo code by title InternalServerError :: {ey.reason}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                    details_message="Error while fetching promo code!")
    except Exception as e:
        logger.error(f"Error while fetching promo code by title :: {e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                    details_message="Error while fetching promo code !")

    if request_body.get('id') is not None:
        filter_list = [{"column": "unique_id", "value": request_body.get('unique_id'), "op": "=="}]
        try:
            promo_code = promo_code_model().get_details_by_filter_list(filter_list)
        except InternalServerError as ey:
            logger.error(
                f"Error while fetching users InternalServerError ::{ey.reason}")
            return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                        details_message="Something went wrong!")
        except Exception as e:
            logger.error(f"Error while fetching users ::{e}")
            return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                        details_message="Something went wrong !")
        if promo_code is None:
            return dict(status_code=http.HTTPStatus.BAD_REQUEST, result=TAG_FAILURE,
                        details_message="Promo code is not found. Please add promo code first!")
        promo_code = promo_code[0]
        # existing_promo_code = promo_code_model().get_promo_code_by_title(request_body.get('title'))
        # if existing_promo_code and (not promo_code or existing_promo_code.title != promo_code.title):
        #      return dict(status_code=http.HTTPStatus.CONFLICT, result=TAG_FAILURE,
        #                  details_message="Duplicate promo code found. Please use a different promo code title.")
    else:
        promo_code = pg_promo_code()
        promo_code.current_usage = 0
        promo_code.unique_id = uuid.uuid4().hex
    promo_code.title = request_body.get('title')
    promo_code.promo_code = request_body.get('promo_code')
    promo_code.discount_type = request_body.get('discount_type')
    promo_code.discount = request_body.get('discount')
    promo_code.max_discount = request_body.get('max_discount', 0)
    promo_code.max_usage = request_body.get('max_usage', 0) if request_body.get('multi_usage', 0) != 0 else 0
    promo_code.expiry_date = request_body.get('expiry_date')
    promo_code.multi_usage = request_body.get('multi_usage', 0)
    promo_code.created_by = session.admin_user_session.user_name

    try:
        db_res = promo_code_model().upsert(promo_code)
        if not db_res.get("status"):
            return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                        detailed_message="Unable to save promo code details!")
        # prepare_and_save_activity_logs(wa_content)
    except Exception as e:
        logger.error(f"Error while saving or updating promo code Exception ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                    detailed_message="Error while saving or updating promo code!")

    logger.debug(f"Exit {method_name}, Success")
    return dict(status_code=http.HTTPStatus.OK, result=TAG_SUCCESS)


def save_or_update_promo_code(promo_code):
    method_name = "save_or_update_promo_code"

    try:
        db_res = promo_code_model().upsert(promo_code)
        if not db_res.get("status"):
            raise InternalServerError(method_name=method_name,
                                      reason="Unable to save campaign whatsapp content details")
        # prepare_and_save_activity_logs(wa_content)
    except InternalServerError as ey:
        logger.error(
            f"Error while saving or updating promo code InternalServerError ::{ey.reason}")
        raise ey
    except Exception as e:
        logger.error(f"Error while saving or updating promo code Exception ::{e}")
        raise e

    logger.debug(f"Exit {method_name}, Success")


def validate_promo_code_details(request_body):
    method_name = "validate_promo_code_details"
    logger.debug(f"Entry {method_name}, request_body: {request_body}")

    if (request_body.get('discount_type') is None or request_body.get('discount_type') not in
            [PromoCodeDiscountType.flat.value, PromoCodeDiscountType.percentage.value]):
        raise BadRequestException(method_name=method_name, reason="Discount type is incorrect")

    if (request_body.get('expiry_date') is None or request_body.get('expiry_date') == "" or
            datetime.strptime(request_body.get('expiry_date'), "%Y-%m-%d").date() < datetime.utcnow().date()):
        raise BadRequestException(method_name=method_name,
                                  reason="Expiry date is not provided/ less than current date !")

    validate_promo_code_title(request_body.get('title'))
    validate_promo_code(request_body.get('promo_code'))
    validate_discount(request_body.get('discount'), request_body.get('discount_type'))

    logger.debug(f"Exit {method_name}, Success")


def validate_promo_code_title(name):
    method_name = "validate_promo_code_title"
    logger.debug(f"Entry {method_name}, name: {name}")
    if name is None:
        raise BadRequestException(method_name=method_name, reason="Title is not provided")
    if len(name) > MAX_ALLOWED_PROMO_CODE_NAME_LENGTH or len(name) < MIN_ALLOWED_PROMO_CODE_NAME_LENGTH:
        raise BadRequestException(method_name=method_name,
                                  reason=F"Title length should be from {MIN_ALLOWED_PROMO_CODE_NAME_LENGTH} to {MAX_ALLOWED_PROMO_CODE_NAME_LENGTH}")

    if is_valid_alpha_numeric_space_under_score(name) is False:
        raise BadRequestException(method_name=method_name,
                                  reason="Title format incorrect, only alphanumeric, space and underscore characters allowed")
    logger.debug(f"Exit {method_name}, Success")


def validate_promo_code(promo_code):
    method_name = "validate_promo_code"
    logger.debug(f"Entry {method_name}, promo_code: {promo_code}")
    if promo_code is None:
        raise BadRequestException(method_name=method_name, reason="Promo code is not provided")
    if len(promo_code) > MAX_ALLOWED_PROMO_CODE_LENGTH or len(promo_code) < MIN_ALLOWED_PROMO_CODE_LENGTH:
        raise BadRequestException(method_name=method_name,
                                  reason=F"Promo code length should be from {MIN_ALLOWED_PROMO_CODE_LENGTH} to {MAX_ALLOWED_PROMO_CODE_LENGTH}")
    logger.debug(f"Exit {method_name}, Success")


def validate_discount(discount, discount_type):
    method_name = "validate_discount"
    logger.debug(f"Entry {method_name}, discount: {discount}")
    if discount is None:
        raise BadRequestException(method_name=method_name, reason="Discount is not provided")
    if int(discount) < 1:
        raise BadRequestException(method_name=method_name,
                                  reason=F"Discount can't be less than 1")
    if discount_type == PromoCodeDiscountType.percentage.value and int(discount) > 100:
        raise BadRequestException(method_name=method_name,
                                  reason=F"Discount can't be greater than 100%")
    logger.debug(f"Exit {method_name}, Success")


def fetch_and_prepare_promo_code():
    method_name = "fetch_and_prepare_promo_code"
    logger.debug(f"Entry {method_name}")

    try:
        promo_code = promo_code_model().get_details_by_filter_list([])
    except InternalServerError as ey:
        logger.error(
            f"Error while fetching users InternalServerError ::{ey.reason}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    except Exception as e:
        logger.error(f"Error while fetching users ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    if promo_code is None:
        return dict(status_code=http.HTTPStatus.BAD_REQUEST, result=TAG_FAILURE,
                    details_message="Promo code is not found. Please add promo code first!")
    # Convert list of model instances to list of dictionaries
    promo_code_list = []
    for promo in promo_code:
        if promo.is_active:
            cta = "<button id=\"deact-{}\" class=\"btn-outline-danger btn-sm mr-1\" onclick=\"deactivatePromoCode('{}')\">Deactivate</button>".format(
                promo.unique_id, promo.unique_id)
        else:
            cta = "<button id=\"act-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"activatePromoCode('{}')\">Activate</button>".format(
                promo.unique_id, promo.unique_id)
        if promo.max_usage == 0 and promo.multi_usage == 1:
            usage_left = '<p style="font-size: 20px;">∞</p>'
        else:
            usage_left = f'{promo.max_usage - promo.current_usage}'
        promo_code_list.append({
            "unique_id": promo.unique_id,
            "title": promo.title,
            "promo_code": promo.promo_code,
            "discount_type": promo.discount_type,
            "discount": promo.discount,
            "max_discount": promo.max_discount,
            "expiry_date": promo.expiry_date.strftime('%d %b %Y, %I:%M %p'),
            "is_active": promo.is_active,
            "multi_usage": promo.multi_usage,
            "created_by": promo.created_by,
            "last_update": promo.ut.strftime('%d %b %Y, %I:%M %p'),
            "usage_left": usage_left,
            "edit": "<button id=\"edit-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"editPromoCode('{}')\">Edit</button>".format(promo.unique_id, promo.unique_id),
            "cta": cta
        })
    return promo_code_list


def fetch_promo_code_by_unique_id(unique_id):
    filter_list = [{"column": "unique_id", "value": unique_id, "op": "=="}]
    try:
        promo_code = promo_code_model().get_details_by_filter_list(filter_list)
    except InternalServerError as ey:
        logger.error(
            f"Error while fetching users InternalServerError ::{ey.reason}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    except Exception as e:
        logger.error(f"Error while fetching users ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    if promo_code is None:
        return dict(status_code=http.HTTPStatus.BAD_REQUEST, result=TAG_FAILURE,
                    details_message="Promo code is not found. Please add promo code first!")
    promo = promo_code[0]
    promo_dict = {
            "title": promo.title,
            "id": promo.id,
            "unique_id": promo.unique_id,
            "promo_code": promo.promo_code,
            "discount_type": promo.discount_type,
            "discount": promo.discount,
            "max_discount": promo.max_discount,
            "max_usage": promo.max_usage,
            "expiry_date": promo.expiry_date.strftime('%d %b %Y, %I:%M %p'),
            "multi_usage": promo.multi_usage
        }
    return promo_dict


def deactivate_promo(unique_id):
    method_name = "deactivate_promo"

    try:
        filter_list = [{"column": "unique_id", "value": unique_id, "op": "=="}]
        promo_code_model().update_by_filter_list(filter_list, dict(is_active=0))
    except Exception as e:
        logger.error(f"Error while deleting user ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)

    logger.debug(f"Exit {method_name}, Success")
    return dict(status_code=http.HTTPStatus.OK, result=TAG_SUCCESS)


def activate_promo(unique_id):
    method_name = "activate_promo"

    try:
        filter_list = [{"column": "unique_id", "value": unique_id, "op": "=="}]
        promo_code = promo_code_model().get_details_by_filter_list(filter_list)
        if promo_code is None or len(promo_code) < 1:
            return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                        detailed_message="Promo code id is incorrect!")
        if promo_code[0].expiry_date.date() < datetime.utcnow().date():
            return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                        detailed_message="Expire time will be greater than current date time!")
        if (promo_code[0].max_usage > 0) and (promo_code[0].max_usage - promo_code[0].current_usage < 1):
            return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                        detailed_message="No usage count left. First increase max usage!")
        promo_code_model().update_by_filter_list(filter_list, dict(is_active=1))
    except InternalServerError as ey:
        logger.error(
            f"Error while fetching users InternalServerError ::{ey.reason}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    except Exception as e:
        logger.error(f"Error while deleting user ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)

    logger.debug(f"Exit {method_name}, Success")
    return dict(status_code=http.HTTPStatus.OK, result=TAG_SUCCESS)

# def prepare_and_save_activity_logs():
#     activity_log_entity = CED_ActivityLog()
#     activity_log_entity.data_source = DataSource.CONTENT.value,
#     activity_log_entity.sub_data_source = SubDataSource.WHATSAPP_CONTENT.value,
#     activity_log_entity.data_source_id = unique_id
#     activity_log_entity.comment = wa_content_his_entity.comment
#     activity_log_entity.filter_id = wa_content.project_id
#     activity_log_entity.history_table_id = wa_content_his_entity.unique_id
#     activity_log_entity.unique_id = uuid.uuid4().hex
#     activity_log_entity.created_by = user_name
#     activity_log_entity.updated_by = user_name
#     CEDActivityLog().save_or_update_activity_log(activity_log_entity)