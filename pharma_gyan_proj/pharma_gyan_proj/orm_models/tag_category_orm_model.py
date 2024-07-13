from pharma_gyan_proj.orm_models.base_model import *


class pg_tag_category(Base, Orm_helper):
    __tablename__ = 'tag_category'

    id = Column("id", Integer, autoincrement=True)
    unique_id = Column("unique_id", String, primary_key=True)
    title = Column("title", String)
    extra = Column("extra", String)
    is_active = Column("is_active", Integer, default=1)
    ct = Column("ct", DateTime, default=datetime.utcnow())
    ut = Column("ut", TIMESTAMP,
                           server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __init__(self, data={}):
        Orm_helper.__init__(self, data)
