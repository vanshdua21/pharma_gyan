from pharma_gyan_proj.orm_models.v2.all_models import Course
from pharma_gyan_proj.utils.sqlalchemy_helper import fetch_count, fetch_rows_with_join, sql_alchemy_connect, save_or_update_merge, fetch_rows_limited, \
    update


class course_model_v2:
    def __init__(self, **kwargs):
        self.database = kwargs.get("db_conf_key", "default")
        self.table = Course
        self.engine = sql_alchemy_connect(self.database)

    def upsert(self, course_model):
        try:
            res = save_or_update_merge(self.engine, course_model)
        except Exception as ex:
            return dict(status=False, response=str(ex))
        return dict(status=True, response=res)

    def get_details_by_filter_list(self, filter_list, columns_list=[], relationships_list=[]):
        res = fetch_rows_with_join(self.engine, self.table, filter_list, columns=columns_list,
                                 relationships=relationships_list)
        if res is None or len(res) <= 0:
            return []
        return res

    def update_by_filter_list(self, filter_list, update_dict):
        return update(self.engine, self.table, filter_list, update_dict)
    
    def fetch_count_by_filter(self, filter_list):
        return fetch_count(self.engine, self.table, filter_list)
