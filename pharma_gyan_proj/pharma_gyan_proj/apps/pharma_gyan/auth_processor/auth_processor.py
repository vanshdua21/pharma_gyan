import datetime
import http
import logging
import secrets
import string
import uuid
from uuid import UUID

from pharma_gyan_proj.apps.pharma_gyan.auth_processor.app_settings import ACCESS_TOKEN_LENGTH, ACCESS_TOKEN_EXPIRY_DAYS
from pharma_gyan_proj.common.constants import TAG_SUCCESS, TAG_FAILURE
from pharma_gyan_proj.db_models.admin_users import admin_users_model
from pharma_gyan_proj.db_models.user_sessions import user_sessions_model
from pharma_gyan_proj.exceptions.failure_exceptions import InternalServerError
from pharma_gyan_proj.orm_models.user_sessions_orm_model import pg_user_sessions

logger = logging.getLogger("apps")


def validate_and_secure_login(request_body):
    method_name = "validate_and_secure_login"
    logger.debug(f"Entry {method_name}, request_body: {request_body}")

    user_name = request_body.get('user_name')
    password = request_body.get('password')

    cur_date_time = datetime.datetime.utcnow()

    filter_list = [{"column": "user_name", "value": user_name, "op": "=="},
                   {"column": "password", "value": password, "op": "=="},
                   {"column": "is_active", "value": 1, "op": "=="}]

    admin_users = admin_users_model().get_details_by_filter_list(filter_list=filter_list)
    if admin_users is None or len(admin_users) == 0:
        logger.error(f"{method_name} :: Unable to found campaign builder details.")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                    detailed_message="Username or password is incorrect!")
    admin_users = admin_users[0]

    if admin_users.expiry_time is not None and admin_users.expiry_time < cur_date_time:
        set_user_in_active(admin_users.unique_id)
        return dict(status_code=http.HTTPStatus.BAD_REQUEST, result=TAG_FAILURE,
                    detailed_message="User Id expired!")

    characters = string.ascii_letters + string.digits
    access_token = ''.join(secrets.choice(characters) for _ in range(ACCESS_TOKEN_LENGTH))

    user_sessions = pg_user_sessions()
    user_sessions.unique_id = uuid.uuid4().hex if request_body.get('unique_id') is None else request_body.get('unique_id')
    user_sessions.user_uuid = admin_users.unique_id
    user_sessions.access_token = access_token
    user_sessions.expiry_time = datetime.datetime.utcnow() + datetime.timedelta(days=ACCESS_TOKEN_EXPIRY_DAYS)

    try:
        db_res = user_sessions_model().upsert(user_sessions)
        if not db_res.get("status"):
            return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                        detailed_message="Unable to save user session details!")
        # prepare_and_save_activity_logs(wa_content)
    except Exception as e:
        logger.error(f"Error while saving or updating promo code Exception ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                    detailed_message="Error while saving or updating user session!")

    logger.debug(f"Exit {method_name}, Success")
    return dict(status_code=http.HTTPStatus.OK, result=TAG_SUCCESS, access_token=access_token)


def set_user_in_active(unique_id):
    method_name = "validate_login"
    logger.debug(f"Entry {method_name}, unique_id: {unique_id}")

    filter_list = [{"column": "unique_id", "value": unique_id, "op": "=="}]
    admin_users_model().update_admin_users(filter_list=filter_list, update_dict=dict(is_active=0))

    logger.debug(f"Exit {method_name}, Success")


def download_database_dump():
    method_name = "download_database_dump"
    try:
        admin_users_model().dump_database()
    except Exception as e:
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR)

    logger.debug(f"Exit {method_name}, Success")
    return dict(status_code=http.HTTPStatus.OK, result=TAG_SUCCESS)