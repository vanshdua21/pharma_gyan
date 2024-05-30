from pharma_gyan_proj.orm_models.base_model import *


class pg_user_permissions(Base, Orm_helper):
    __tablename__ = 'user_permissions'

    id = Column("id", Integer, autoincrement=True)
    unique_id = Column("unique_id", String, primary_key=True)
    page = Column("page", String)
    ct = Column("ct", DateTime, default=datetime.utcnow())

    def __init__(self, data={}):
        Orm_helper.__init__(self, data)
