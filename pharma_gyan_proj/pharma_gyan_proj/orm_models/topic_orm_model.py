from pharma_gyan_proj.orm_models.base_model import *


class pg_topic(Base, Orm_helper):
    __tablename__ = 'topic'

    id = Column("id", Integer, autoincrement=True, primary_key=True)
    unique_id = Column("unique_id", String)
    client_id = Column("client_id", String)
    title = Column("title", String)
    description = Column("description", String)
    version = Column("version", Integer)
    is_active = Column("is_active", Integer, default='0')
    created_by = Column("created_by", String)
    ct = Column("ct", DateTime, default=datetime.utcnow)
    ut = Column("ut", TIMESTAMP,
                server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))


    def __init__(self, data={}):
        Orm_helper.__init__(self, data)

