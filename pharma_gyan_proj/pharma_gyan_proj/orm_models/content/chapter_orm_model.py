from pharma_gyan_proj.orm_models.base_model import *
from sqlalchemy import Column, Integer, String, Text

class pg_chapter(Base, Orm_helper):
    __tablename__ = 'chapter'

    id = Column("id", Integer, autoincrement=True)
    unique_id = Column("unique_id", String, primary_key=True)
    client_id = Column("client_id", String)
    title = Column("title", String)
    content = Column("content", Text)
    mark_as_free = Column("mark_as_free", Integer, default=0)
    version = Column("version", Integer)
    is_active = Column("is_active", Integer, default=0)
    created_by = Column("created_by", String)
    ct = Column("ct", DateTime, default=datetime.utcnow())

    def __init__(self, data={}):
        Orm_helper.__init__(self, data)
