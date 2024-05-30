from pharma_gyan_proj.orm_models.base_model import *


class pg_user_sessions(Base, Orm_helper):
    __tablename__ = 'user_sessions'

    id = Column("id", Integer, autoincrement=True)
    unique_id = Column("unique_id", String, primary_key=True)
    user_uuid = Column("user_uuid", String)
    access_token = Column("access_token", String)
    expiry_time = Column("expiry_time", DateTime)
    ct = Column("ct", DateTime, default=datetime.utcnow())

    def __init__(self, data={}):
        Orm_helper.__init__(self, data)
