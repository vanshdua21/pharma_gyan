from pharma_gyan_proj.orm_models.base_model import *


class pg_topic_chapter_mapping(Base):
    __tablename__ = 'topic_chapter_mapping'
    id = Column(Integer, primary_key=True, autoincrement=True)
    unique_id = Column(String(255), unique=True, nullable=False)
    chapter_id = Column(Integer, nullable=False)
    topic_id = Column(String(255), nullable=False)
    order = Column(Integer, nullable=False)
    chap_version = Column(Integer, nullable=False)
    topic_version = Column(Integer, nullable=False)
    ct = Column(DateTime, default=datetime.utcnow)
    ut = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


    def __init__(self, data={}):
        Orm_helper.__init__(self, data)