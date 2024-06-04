from pharma_gyan_proj.orm_models.base_model import *


class pg_promo_code(Base, Orm_helper):
    __tablename__ = 'promo_code'

    id = Column("id", Integer, autoincrement=True, primary_key=True)
    title = Column("title", String)
    unique_id = Column("unique_id", String)
    promo_code = Column("promo_code", String)
    discount_type = Column("discount_type", String)
    discount = Column("discount", Integer)
    max_discount = Column("max_discount", Integer)
    expiry_date = Column("expiry_date", DateTime)
    max_usage = Column("max_usage", String)
    current_usage = Column("current_usage", String)
    is_active = Column("is_active", Integer, default=1)
    is_public = Column("is_public", Integer, default=1)
    multi_usage = Column("multi_usage", Integer, default=1)
    created_by = Column("created_by", String)
    ct = Column("ct", DateTime, default=datetime.utcnow())
    ut = Column("ut", TIMESTAMP,
                           server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __init__(self, data={}):
        Orm_helper.__init__(self, data)
