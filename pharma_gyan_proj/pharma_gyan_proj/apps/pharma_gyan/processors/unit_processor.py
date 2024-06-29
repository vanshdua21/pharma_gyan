import http
import json
import logging
from urllib.parse import unquote_plus
import uuid
from datetime import datetime
from django.core.files.storage import FileSystemStorage

from pharma_gyan_proj.common.constants import TAG_FAILURE, TAG_SUCCESS, AdminUserPermissionType
from pharma_gyan_proj.exceptions.failure_exceptions import BadRequestException, InternalServerError
from pharma_gyan_proj.db_models.unit_model import unit_model
from pharma_gyan_proj.orm_models.content_models import PgCourse, PgSemester, PgSubject, PgUnit, PgChapter

logger = logging.getLogger("apps")

def prepare_and_save_unit(request_body):
    method_name = "prepare_and_save_unit"
    logger.debug(f"Entry {method_name}, request_body: {request_body}")

    unit = PgUnit()
    if (request_body.get('id')):
        unit.id = request_body.get('id')
    unit.unique_id = uuid.uuid4().hex if request_body.get('unique_id') is None else request_body.get('unique_id')
    unit.title = request_body.get('title')
    if (request_body.get('ct')):
        unit.ct = request_body.get('ct')
        
    unit.chapters = []
    chaptersBody = request_body.get('chapters')
    if chaptersBody:
        for chap in chaptersBody:
            chapter = PgChapter()
            chapter.id = chap.get('id')
            chapter.unique_id = uuid.uuid4().hex
            chapter.title = chap.get('title')
            chapter.content = chap.get('content')
            chapter.index = chap.get('index')
            unit.chapters.append(chapter)
    
    try: 
        save_or_update_unit(unit)
    except Exception as e:
        logger.error(f"Error while saving or updating unit ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    
    logger.debug(f"Exit {method_name}, Success")
    return dict(status_code=http.HTTPStatus.OK, result=TAG_SUCCESS)

def save_or_update_unit(unit):
    method_name = "save_or_update_course"

    db_res = unit_model().upsert(unit)
    if not db_res.get("status"):
        raise InternalServerError(method_name=method_name,
                                    reason=db_res.get("response"))

    logger.debug(f"Exit {method_name}, Success")

def fetch_units(filter_list=[], relationships_list=[]):
    method_name = "fetch_units"

    try:
        db_res = unit_model().get_details_by_filter_list(filter_list, relationships_list = relationships_list)
    except InternalServerError as ey:
        logger.error(
            f"Error while fetching unit InternalServerError ::{ey.reason}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)
    except Exception as e:
        logger.error(f"Error while unit courses ::{e}")
        return dict(status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR, result=TAG_FAILURE)

    logger.debug(f"Exit {method_name}, Success")
    return db_res


def fetch_unit_from_id(unit_id):
    filter_list = [{"column": "unique_id", "value": unit_id, "op": "=="}]
    relationships_list = ["chapters"]
    units = fetch_units(filter_list, relationships_list)
    if (len(units) == 0):
        return None
    unit = units[0]
    chapters = []
    ch = PgChapter()
    ch.title = 'Chapte 1'
    ch.id = 1
    ch.unique_id = '664ae13317ef4ce486770bc26e6dd041'
    ch.index = 0
    chapters.append(ch)
    
    ch2 = PgChapter()
    ch2.title = 'Chapte 2'
    ch2.id = 2
    ch2.unique_id = '664ae13317ef4ce486770bc26e6dd042'
    ch2.index = 1
    chapters.append(ch2)
    
    ch3 = PgChapter()
    ch3.title = 'Chapte 3'
    ch3.id = 3
    ch3.unique_id = '664ae13317ef4ce486770bc26e6dd043'
    ch3.index = 2
    chapters.append(ch3)
    
    unit.chapters = chapters
    # Convert list of model instances to list of dictionaries
    unit_json = unit.to_json()
    return unit_json