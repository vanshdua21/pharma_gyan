import datetime
from pharma_gyan_proj.utils.database_utils import *
from pharma_gyan_proj.utils.common_utils import nested_path_get
import logging as logger

from django.conf import settings

MYSQL_DB_CONFIG = settings.DATABASES

class PolyglotConfig:
    def __init__(self):
        self.database_config = MYSQL_DB_CONFIG.get("default")
        self.table_name = "polyglot_config"

    def get_config_using_query_params(self, query_parameters):
        connection_obj = get_connection(self.database_config)
        try:
            sql = f"SELECT * FROM {self.table_name} a WHERE a.type = %(type)s"
            if "name" in query_parameters:
                sql += " AND a.name = %(name)s"
            if "version" in query_parameters:
                sql += " AND a.version = %(version)s"
            if "bank" in query_parameters:
                sql += " AND a.bank = %(bank)s"
            result = execute_select(sql, query_parameters, connection_obj)
            return result
        except Exception as e:
            logger.error(
                    f'Error thrown while selecting query : {sql}, message: {str(e)}, log_key: get_attempt_by_rid')
            return None

    def get_config_using_config_name_and_type(self, type=None, name=None):
        connection_obj = get_connection(self.database_config)
        try:
            sql = f"SELECT * FROM {self.table_name} a WHERE a.type = %(type)s"
            if "name" in query_parameters:
                sql += " AND a.name = %(name)s"
            if "version" in query_parameters:
                sql += " AND a.version = %(version)s"
            result = execute_select(sql, query_parameters, connection_obj)
            return result
        except Exception as e:
            logger.error(
                    f'Error thrown while selecting query : {sql}, message: {str(e)}, log_key: get_attempt_by_rid')
            return None

    def latest_config_version(self, query_parameters):
        connection_obj = get_connection(self.database_config)
        try:
            sql = f"SELECT version FROM {self.table_name} a WHERE a.type = %(type)s"
            if "name" in query_parameters:
                sql += " AND a.name = %(name)s"
            sql += " ORDER BY version DESC LIMIT 1"
            result = execute_select(sql, query_parameters, connection_obj)
            if result is None or len(result) == 0:
                return 0
            return result[0].get("version")
        except Exception as e:
            logger.error(
                    f'Error thrown while selecting query : {sql}, message: {str(e)}, log_key: get_attempt_by_rid')
            return None

    def insert_config(self, columns, values):
        connection_obj = get_connection(self.database_config)
        try:
            params = {
                "columns" : columns,
                "values" : values
            }
            rows_affected = execute_insert(connection_obj, self.table_name, params)
            return rows_affected
        except Exception as e:
            logger.error(
                    f'Error thrown while inserting query : {self.table_name}, message: {str(e)}, log_key: insert_polyglot_config')
            return None

    def update_config_using_id(self,id, upd_dict):
        connection_obj = get_connection(self.database_config)
        try:
            where_dict = {
                'id': id
            }
            rows_affected = update_data_by_id(connection_obj,self.table_name, where_dict, upd_dict)
            return rows_affected
        except Exception as e:
            logger.error(
                    f'Error thrown while updating query : {self.table_name}, message: {str(e)}, log_key: update_attempt_via_id')
            return None

    def delete_attempt_by_id(self, ids):
        connection_obj = get_connection(self.database_config)
        query_params  = {}
        try:
            if len(ids) == 1:
                sql = f"DELETE FROM {self.table_name} WHERE id IN ('{ids[0]}')"
            else:
                sql = f"DELETE FROM {self.table_name} WHERE id IN {ids}"
            result = execute_delete(connection_obj,sql, query_params)
            return result
        except Exception as e:
            logging.error(
                    f'Error thrown while selecting query : {sql}, message: {str(e)}, log_key: delete_attempt_log_by_rid')
            return None

    def execute_sql_statement(self, sql):
        connection_obj = get_connection(self.database_config)
        try:
            query_parameters = {}
            result = execute_select(sql, query_parameters, connection_obj)
            return result
        except Exception as e:
            logger.error(
                    f'Error thrown while selecting query : {sql}, message: {str(e)}, log_key: execute_sql_statement')
            return None
