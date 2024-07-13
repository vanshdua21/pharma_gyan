import http
import json
import logging
from urllib.parse import unquote_plus
import uuid
from datetime import datetime

from pharma_gyan_proj.common.constants import TAG_FAILURE, TAG_SUCCESS, AdminUserPermissionType
from pharma_gyan_proj.db_models.admin_users import admin_users_model
from pharma_gyan_proj.exceptions.failure_exceptions import BadRequestException, InternalServerError
from pharma_gyan_proj.orm_models.admin_users_orm_model import pg_admin_users

logger = logging.getLogger("apps")


def prepare_and_save_user(request_body):
    method_name = "prepare_and_save_admin_user"
    logger.debug(f"Entry {method_name}, request_body: {request_body}")

    admin_user = pg_admin_users()
    if (request_body.get('id')):
        admin_user.id = request_body.get('id')
    else:
        try:
            existing_admin_user = admin_users_model().get_user_by_un_or_mn(request_body.get('phone'),
                                                                           request_body.get('userName'))
            if existing_admin_user is not None and len(existing_admin_user) > 0:
                if request_body.get('id') is None or existing_admin_user[0].unique_id != request_body.get('unique_id'):
                    return dict(status_code=http.HTTPStatus.CONFLICT, result=TAG_FAILURE,
                                details_message="Duplicate admin user found. Please use a different user name or mobile number!")
        except InternalServerError as ey:
            logger.error(f"Error while fetching admin user by user_name InternalServerError :: {ey.reason}")
            return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                        details_message="Error while fetching admin user!")
        except Exception as e:
            logger.error(f"Error while fetching admin user by user_name Exception :: {e}")
            return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                        details_message="Error while fetching admin user !")

    admin_user.unique_id = uuid.uuid4().hex if request_body.get('unique_id') is None else request_body.get('unique_id')
    admin_user.email_id = request_body.get('email')
    admin_user.mobile_number = request_body.get('phone')
    admin_user.password = request_body.get('pass')
    admin_user.permissions = ', '.join(json.loads(request_body.get('perm', [])))
    admin_user.user_name = request_body.get('userName')
    admin_user.display_name = unquote_plus(request_body.get('displayName'))
    admin_user.client_id = 'cd6b7678-3ea3-11ef-a04f-5a57a4320fb5'
    if (request_body.get('is_active')):
        admin_user.is_active = request_body.get('is_active')
    if (request_body.get('ct')):
        admin_user.ct = request_body.get('ct')

    save_or_update_admin_user(admin_user)

    logger.debug(f"Exit {method_name}, Success")
    return dict(status_code=http.HTTPStatus.OK, result=TAG_SUCCESS)


def save_or_update_admin_user(admin_user):
    method_name = "save_or_update_user"

    try:
        db_res = admin_users_model().upsert(admin_user)
        if not db_res.get("status"):
            raise InternalServerError(method_name=method_name,
                                      reason=db_res.get("response"))
    except InternalServerError as ey:
        logger.error(
            f"Error while saving or updating user InternalServerError ::{ey.reason}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    except Exception as e:
        logger.error(f"Error while saving or updating user ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)

    logger.debug(f"Exit {method_name}, Success")

def fetch_and_prepare_users():
    method_name = "fetch_and_prepare_users"
    logger.debug(f"Entry {method_name}")
    users = fetch_users()
    # Convert list of model instances to list of dictionaries
    users_list = []
    for user in users:
        user_permission = []
        permissions_list = user.permissions.split(', ') if user.permissions != '' else []
        for permission in permissions_list:
            user_permission.append(AdminUserPermissionType[permission].value)
        users_list.append({
            "unique_id": user.unique_id,
            "display_name": user.display_name,
            "email_id": user.email_id,
            "user_name": user.user_name,
            "mobile_number": user.mobile_number,
            "password": user.password,
            "permissions": ", ".join(user_permission) if len(user_permission) > 0 else '-',
            "is_active": user.is_active,
            "edit": "<button id=\"edit-{}\" class=\"btn-outline-success btn-sm mr-1\" onclick=\"editUser('{}')\">Edit</button>".format(user.unique_id, user.unique_id),
            "del": "<button id=\"del-{}\" class=\"btn-outline-danger btn-sm mr-1\" onclick=\"delUser('{}')\">Delete</button>".format(user.unique_id, user.unique_id)
        })
    return users_list

def fetch_users(filter_list=[]):
    method_name = "fetch_users"

    try:
        db_res = admin_users_model().get_details_by_filter_list(filter_list)
    except InternalServerError as ey:
        logger.error(
            f"Error while fetching users InternalServerError ::{ey.reason}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    except Exception as e:
        logger.error(f"Error while fetching users ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)

    logger.debug(f"Exit {method_name}, Success")
    return db_res

def fetch_user_from_id(user_id):
    filter_list = [{"column": "unique_id", "value": user_id, "op": "=="}]
    users = fetch_users(filter_list)
    if (len(users) == 0):
        return None
    user = users[0]
    permissions = {permission.name: 0 for permission in AdminUserPermissionType}
    set_permissions = set(user.permissions.split(', '))
    for perm in set_permissions:
        permissions[perm] = 1
    # Convert list of model instances to list of dictionaries
    users_list = []
    for user in users:
        users_list.append({
            "id": user.id,
            "unique_id": user.unique_id,
            "display_name": user.display_name,
            "email_id": user.email_id,
            "user_name": user.user_name,
            "mobile_number": user.mobile_number,
            "password": user.password,
            "permissions": permissions,
            "is_active": user.is_active,
            "ct": user.ct
        })
    return users_list[0]

def delete_user(user_id):
    method_name = "delete_user"

    try:
        filter_list = [{"column": "unique_id", "value": user_id, "op": "=="}]
        db_res = admin_users_model().delete(filter_list)
    except InternalServerError as ey:
        logger.error(
            f"Error while deleting user InternalServerError ::{ey.reason}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    except Exception as e:
        logger.error(f"Error while deleting user ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)

    logger.debug(f"Exit {method_name}, Success")
    return dict(status_code=http.HTTPStatus.OK, result=TAG_SUCCESS)