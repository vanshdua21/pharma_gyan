from pharma_gyan_proj.utils.sqlalchemy_helper import sql_alchemy_connect, save_or_update_merge, fetch_rows_limited, \
    update, execute_query
from pharma_gyan_proj.db_models.pharma_gyan import pg_entity_tag


class entity_tag_model:
    def __init__(self, **kwargs):
        self.database = kwargs.get("db_conf_key", "default")
        self.table = pg_entity_tag
        self.engine = sql_alchemy_connect(self.database)

    def upsert(self, entity_tag_model):
        try:
            res = save_or_update_merge(self.engine, entity_tag_model)
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


    def get_entity_tag_by_title_and_tag_category(self, title, tag_category):
        try:
            query = f"""
                    SELECT id from entity_tag WHERE title = '{title}' and tag_category_id = '{tag_category}'
                    """
            res = execute_query(self.engine, query)
            return res
        except:
            return None
