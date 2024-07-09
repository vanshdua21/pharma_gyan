from pharma_gyan_proj.orm_models.base_model import *


class pg_entity_tag(Base, Orm_helper):
    __tablename__ = 'entity_tag'

    id = Column("id", Integer, autoincrement=True)
    title = Column("title", String)
    unique_id = Column("unique_id", String, primary_key=True)
    client_id = Column("client_id", String)
    description = Column("description", String)
    level = Column("level", Integer)
    is_active = Column("is_active", Integer, default=1)
    created_by = Column("created_by", String)
    ct = Column("ct", DateTime, default=datetime.utcnow())
    ut = Column("ut", TIMESTAMP,
                           server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __init__(self, data={}):
        Orm_helper.__init__(self, data)
