import logging
from datetime import datetime

from pharma_gyan_proj import settings
from pharma_gyan_proj.common.constants import TAG_FAILURE, TAG_GENERATE_OTP
from pharma_gyan_proj.db_models.admin_users import admin_users_model
from pharma_gyan_proj.db_models.user_permissions import user_permissions_model
from pharma_gyan_proj.db_models.user_sessions import user_sessions_model
from pharma_gyan_proj.exceptions.failure_exceptions import MethodPermissionValidationException, \
    UnauthorizedException, ValidationFailedException, BadRequestException, NotFoundException, InternalServerError, \
    OtpRequiredException
from django.http import HttpResponse
from django.template.loader import render_to_string

import http
import json
logger = logging.getLogger("apps")


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class HttpRequestInterceptor:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path not in [settings.LOGIN_PATH, settings.SECURE_LOGIN_PATH]:
            response = self.prehandle(request)
            if response is not None:
                status_code = response.pop("status_code", http.HTTPStatus.BAD_REQUEST)
                return HttpResponse(json.dumps(response, default=str), status=status_code, content_type="application/json")

        response = self.get_response(request)

        return response

    def prehandle(self,request):
        session_obj = Session()
        session_obj.set_admin_user_session_object(None)
        session_obj.set_admin_user_permissions({})
        access_token = request.COOKIES.get('access_token')
        if access_token is None:
            return dict(status_code=http.HTTPStatus.NOT_FOUND, result=TAG_FAILURE,
                        detailed_message="Page not found!")
        cur_date_time = datetime.utcnow()
        filter_list = [{"column": "access_token", "value": access_token, "op": "=="},
                       {"column": "expiry_time", "value": cur_date_time, "op": ">"}]

        admin_user_session = user_sessions_model().get_details_by_filter_list(filter_list=filter_list)
        if admin_user_session is None or len(admin_user_session) == 0:
            return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                        detailed_message="Unable to get user session details!")
        ## todo throughback to login screen
        admin_user_session = admin_user_session[0]
        filter_list = [{"column": "unique_id", "value": admin_user_session.user_uuid, "op": "=="}]

        admin_user = admin_users_model().get_details_by_filter_list(filter_list=filter_list)
        if admin_user is None or len(admin_user) == 0:
            return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE,
                        detailed_message="Unable to get admin user details!")
        admin_user = admin_user[0]
        session_obj.set_admin_user_session_object(admin_user)
        session_obj.set_admin_user_permissions(admin_user.permissions)

    def process_exception(self,request, exception):
        if isinstance(exception,UnauthorizedException):
            response = dict(result=TAG_FAILURE, details_message="admin_user not logged in")
            return HttpResponse(json.dumps(response),
                                content_type="application/json",
                                status=http.HTTPStatus.UNAUTHORIZED)
        elif isinstance(exception,MethodPermissionValidationException):
            response = dict(result=TAG_FAILURE, details_message="Forbidden")
            return HttpResponse(json.dumps(response),
                                content_type="application/json",
                                status=http.HTTPStatus.FORBIDDEN)
        elif isinstance(exception,ValidationFailedException):
            response = dict(result=TAG_FAILURE, details_message=exception.reason, data=exception.data)
            return HttpResponse(json.dumps(response),
                                content_type="application/json",
                                status=http.HTTPStatus.BAD_REQUEST)
        elif isinstance(exception,BadRequestException):
            response = dict(result=TAG_FAILURE, details_message=exception.reason)
            return HttpResponse(json.dumps(response),
                                content_type="application/json",
                                status=http.HTTPStatus.BAD_REQUEST)
        elif isinstance(exception,NotFoundException):
            response = dict(result=TAG_FAILURE, details_message=exception.reason)
            return HttpResponse(json.dumps(response),
                                content_type="application/json",
                                status=http.HTTPStatus.BAD_REQUEST)
        elif isinstance(exception, InternalServerError):
            response = dict(result=TAG_FAILURE, details_message=exception.reason)
            return HttpResponse(json.dumps(response),
                                content_type="application/json",
                                status=http.HTTPStatus.INTERNAL_SERVER_ERROR)
        elif isinstance(exception, OtpRequiredException):
            response = dict(result=TAG_GENERATE_OTP, data=exception.data, details_message="please generate and validate otp first")
            return HttpResponse(json.dumps(response),
                                content_type="application/json",
                                status=http.HTTPStatus.OK)


class Session(metaclass=Singleton):

    admin_user_session = None
    project_permissions = {}

    def __init__(self):
        self.admin_user_session = None
        self.project_permissions = {}

    def set_admin_user_session_object(self,admin_user_session):
        self.admin_user_session = admin_user_session

    def get_admin_user_session_object(self):
        return self.admin_user_session

    def del_admin_user_session_object(self):
        self.admin_user_session = None

    def set_admin_user_permissions(self,permissions):
        self.project_permissions = permissions

    def get_admin_user_permissions(self):
        return self.project_permissions

    def del_admin_user_permissions(self):
        self.project_permissions = None
