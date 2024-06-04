from pharma_gyan_proj.orm_models.base_model import *


class pg_admin_users(Base, Orm_helper):
    __tablename__ = 'admin_users'

    id = Column("id", Integer, autoincrement=True)
    unique_id = Column("unique_id", String, primary_key=True)
    email_id = Column("email_id", String)
    expiry_time = Column("expiry_time", DateTime)
    mobile_number = Column("mobile_number", String)
    password = Column("password", String)
    permissions = Column("permissions", String)
    is_active = Column("is_active", Integer, default=1)
    user_name = Column("user_name", String)
    display_name = Column("display_name", String)
    created_by = Column("created_by", String)
    ct = Column("ct", DateTime, default=datetime.utcnow())

    def __init__(self, data={}):
        Orm_helper.__init__(self, data)
