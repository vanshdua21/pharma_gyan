from pharma_gyan_proj.orm_models.base_model import *


class pg_course(Base, Orm_helper):
    __tablename__ = 'course'

    id = Column("id", Integer, autoincrement=True)
    unique_id = Column("unique_id", String, primary_key=True)
    title = Column("title", String)
    description = Column("description", text)
    thumbnail_url = Column("thumbnail_url", String)
    created_by = Column("created_by", String)
    ct = Column("ct", DateTime, default=datetime.utcnow())

    def __init__(self, data={}):
        Orm_helper.__init__(self, data)
