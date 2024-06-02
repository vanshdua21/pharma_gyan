import http
import logging
import uuid
from datetime import datetime

from pharma_gyan_proj.apps.pharma_gyan.app_settings import MAX_ALLOWED_PROMO_CODE_NAME_LENGTH, \
    MIN_ALLOWED_PROMO_CODE_LENGTH, MAX_ALLOWED_PROMO_CODE_LENGTH, MIN_ALLOWED_PROMO_CODE_NAME_LENGTH
from pharma_gyan_proj.common.comman import is_valid_alpha_numeric_space_under_score
from pharma_gyan_proj.common.constants import TAG_FAILURE, TAG_SUCCESS, PromoCodeDiscountType
from pharma_gyan_proj.db_models.promo_code_model import promo_code_model
from pharma_gyan_proj.orm_models.promo_code_orm_model import pg_promo_code
from pharma_gyan_proj.exceptions.failure_exceptions import BadRequestException, InternalServerError

logger = logging.getLogger("apps")


def prepare_and_save_promo_code(request_body):
    method_name = "prepare_and_save_promo_code"
    logger.debug(f"Entry {method_name}, request_body: {request_body}")

    validate_promo_code_details(request_body)

    promo_code = pg_promo_code()
    promo_code.unique_id = uuid.uuid4().hex if request_body.get('unique_id') is None else request_body.get('unique_id')
    promo_code.title = request_body.get('title')
    promo_code.promo_code = request_body.get('promo_code')
    promo_code.discount_type = request_body.get('discount_type')
    promo_code.discount = request_body.get('discount')
    promo_code.max_discount = request_body.get('max_discount', 0)
    promo_code.max_usage = request_body.get('max_usage', 0)
    promo_code.expiry_date = request_body.get('expiry_date')
    promo_code.is_public = request_body.get('is_public', 0)
    promo_code.multi_usage = request_body.get('multi_usage', 0)
    promo_code.created_by = request_body.user

    try:
        db_res = promo_code_model().upsert(promo_code)
        if not db_res.get("status"):
            return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                        detailed_message="Unable to save campaign whatsapp content details!")
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
            datetime.strptime(request_body.get('expiry_date'), "%Y-%m-%d %H:%M:%S").date() < datetime.utcnow()):
        raise BadRequestException(method_name=method_name, reason="Content text is not provided")

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
    if discount < 1:
        raise BadRequestException(method_name=method_name,
                                  reason=F"Discount can't be less than 1")
    if discount_type == PromoCodeDiscountType.percentage.value and discount > 100:
        raise BadRequestException(method_name=method_name,
                                  reason=F"Discount can't be greater than 100%")
    logger.debug(f"Exit {method_name}, Success")

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