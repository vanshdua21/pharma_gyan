from pharma_gyan_proj.utils.sqlalchemy_helper import sql_alchemy_connect, save_or_update_merge, fetch_rows_limited, \
    update, execute_query, bulk_insert
from pharma_gyan_proj.orm_models.topic_chapter_mapping_orm_model import pg_topic_chapter_mapping


class topic_chapter_mapping_model:
    def __init__(self, **kwargs):
        self.database = kwargs.get("db_conf_key", "default")
        self.table = pg_topic_chapter_mapping
        self.engine = sql_alchemy_connect(self.database)

    def upsert(self, topic_chapter_mapping_model):
        try:
            res = save_or_update_merge(self.engine, topic_chapter_mapping_model)
        except Exception as ex:
            return dict(status=False, response=str(ex))
        return dict(status=True, response=res)

    def bulk_save_mapping(self, topic_chapter_mapping):
        try:
            response = bulk_insert(self.engine, topic_chapter_mapping)
        except Exception as ex:
            return dict(status=False, message=str(ex))
        return dict(status=True, response=response)

    def get_details_by_filter_list(self, filter_list, columns_list=[], relationships_list=[]):
        res = fetch_rows_limited(self.engine, self.table, filter_list, columns=columns_list,
                                 relationships=relationships_list)
        if res is None or len(res) <= 0:
            return None
        return res

    def update_by_filter_list(self, filter_list, update_dict):
        return update(self.engine, self.table, filter_list, update_dict)
