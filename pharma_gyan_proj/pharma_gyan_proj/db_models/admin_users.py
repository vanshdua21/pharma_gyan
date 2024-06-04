import json
import subprocess

from pharma_gyan_proj import settings
from pharma_gyan_proj.orm_models.admin_users_orm_model import pg_admin_users
from pharma_gyan_proj.utils.sqlalchemy_helper import sql_alchemy_connect, save_or_update_merge, fetch_rows_limited, \
    update, execute_query, delete


class admin_users_model:
    def __init__(self, **kwargs):
        self.database = kwargs.get("db_conf_key", "default")
        self.table = pg_admin_users
        self.engine = sql_alchemy_connect(self.database)

    def upsert(self, admin_user_model):
        try:
            res = save_or_update_merge(self.engine, admin_user_model)
        except Exception as ex:
            return dict(status=False, response=str(ex))
        return dict(status=True, response=res)

    def get_details_by_filter_list(self, filter_list=[], columns_list=[], relationships_list=[]):
        res = fetch_rows_limited(self.engine, self.table, filter_list, columns=columns_list,
                                 relationships=relationships_list)
        return res

    def delete(self, filter_list):
        try:
            res = delete(self.engine, self.table, filter_list)
        except Exception as ex:
            return dict(status=False, response=str(ex))
        return dict(status=True, response=res)

    def update_admin_users(self, filter_list, update_dict):
        return update(self.engine, self.table, filter_list, update_dict)

    def fetch_user_detail_by_access_token(self, access_token, curr_date_time):
        query = f"""SELECT au.unique_id as user_uuid, au.first_name as first_name, au.middle_name as middle_name, 
        au.last_name as last_name, au.email_id as email_id, au.mobile_number as mobile_number, au.user_name as 
        user_name, au.expiry_time as user_expiry, au.permissions as admin_user_permission, us.access_token as 
        access_token, us.expiry_time as session_expiry_time FROM admin_users au join user_sessions us on au.unique_id = 
        us.user_uuid where us.access_token = '{access_token}' and us.expiry_time > '{curr_date_time}'"""
        res = execute_query(self.engine, query)
        return res

    def dump_database(self):
        dump_command = f"mysqldump -u {settings.DATABASES[self.database]['USER']} -p{settings.DATABASES[self.database]['PASSWORD']} -h {settings.DATABASES[self.database]['HOST']} {settings.DATABASES[self.database]['NAME']} > {settings.DATABASES[self.database]['NAME']}.sql"
        subprocess.run(dump_command, shell=True, check=True)
