from pharma_gyan_proj.orm_models.base_model import *


class pg_subject(Base, Orm_helper):
    __tablename__ = 'subject'

    id = Column("id", Integer, autoincrement=True)
    unique_id = Column("unique_id", String, primary_key=True)
    name = Column("name", String)
    semester_id = Column("semester_id", Integer)
    created_by = Column("created_by", String)
    ct = Column("ct", DateTime, default=datetime.utcnow())

    def __init__(self, data={}):
        Orm_helper.__init__(self, data)
