from pharma_gyan_proj.orm_models.tag_category_orm_model import pg_tag_category
from pharma_gyan_proj.utils.sqlalchemy_helper import sql_alchemy_connect, save_or_update_merge, fetch_rows_limited, \
    update, execute_query


class tag_category_model:
    def __init__(self, **kwargs):
        self.database = kwargs.get("db_conf_key", "default")
        self.table = pg_tag_category
        self.engine = sql_alchemy_connect(self.database)

    def upsert(self, tag_category_model):
        try:
            res = save_or_update_merge(self.engine, tag_category_model)
        except Exception as ex:
            return dict(status=False, response=str(ex))
        return dict(status=True, response=res)

    def get_details_by_filter_list(self, filter_list, columns_list=[], relationships_list=[]):
        res = fetch_rows_limited(self.engine, self.table, filter_list, columns=columns_list,
                                 relationships=relationships_list)
        if res is None or len(res) <= 0:
            return None
        return res

    def update_by_filter_list(self, filter_list, update_dict):
        return update(self.engine, self.table, filter_list, update_dict)

    def get_tag_category_by_title(self, title):
        filter_list = [{"column": "title", "value": title, "op": "=="}]
        return self.get_details_by_filter_list(filter_list)

    def get_tag_category_by_unique_id(self, unique_id):
        filter_list = [{"column": "unique_id", "value": unique_id, "op": "=="},
                       {"column": "is_active", "value": 1, "op": "=="}]
        return self.get_details_by_filter_list(filter_list)
