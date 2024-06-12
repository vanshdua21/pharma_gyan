from pharma_gyan_proj.orm_models.base_model import *


class pg_chapter(Base, Orm_helper):
    __tablename__ = 'chapter'

    id = Column("id", Integer, autoincrement=True)
    unique_id = Column("unique_id", String, primary_key=True)
    title = Column("title", String)
    content = Column("content", text)
    unit_id = Column("unit_id", Integer)
    created_by = Column("created_by", String)
    ct = Column("ct", DateTime, default=datetime.utcnow())

    def __init__(self, data={}):
        Orm_helper.__init__(self, data)

