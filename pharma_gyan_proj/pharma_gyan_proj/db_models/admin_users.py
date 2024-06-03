import json
from pharma_gyan_proj.orm_models.admin_users_orm_model import pg_admin_users
from pharma_gyan_proj.utils.sqlalchemy_helper import delete, sql_alchemy_connect, save_or_update_merge, fetch_rows_limited


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
