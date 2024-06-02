from pharma_gyan_proj.orm_models.admin_users_orm_model import pg_admin_users
from pharma_gyan_proj.utils.sqlalchemy_helper import sql_alchemy_connect, save_or_update_merge, fetch_rows_limited, \
    update, execute_query


class admin_users_model:
    def __init__(self, **kwargs):
        self.database = kwargs.get("db_conf_key", "default")
        self.table = pg_admin_users
        self.engine = sql_alchemy_connect(self.database)

    def upsert(self, promo_code_model):
        try:
            res = save_or_update_merge(self.engine, promo_code_model)
        except Exception as ex:
            return dict(status=False, response=str(ex))
        return dict(status=True, response=res)

    def get_details_by_filter_list(self, filter_list, columns_list=[], relationships_list=[]):
        res = fetch_rows_limited(self.engine, self.table, filter_list, columns=columns_list,
                                 relationships=relationships_list)
        if res is None or len(res) <= 0:
            return None
        return res

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
