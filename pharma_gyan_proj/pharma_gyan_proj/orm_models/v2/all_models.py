from pharma_gyan_proj.orm_models.base_model import *

class Course(Base):
    __tablename__ = 'course'
    id = Column(Integer, primary_key=True, autoincrement=True)
    unique_id = Column(String(255), unique=True, nullable=False)
    client_id = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    created_by = Column(String(64))
    is_active = Column(Boolean, default=False)
    version = Column(Integer, nullable=False)
    ct = Column(DateTime, default=datetime.utcnow)
    ut = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    tags = relationship('CourseTagMapping', back_populates='course', cascade='all, delete, delete-orphan')
    topics = relationship('CourseTopicMapping', back_populates='course', cascade='all, delete, delete-orphan')

class CourseTagMapping(Base):
    __tablename__ = 'course_tag_mapping'
    id = Column(Integer, primary_key=True, autoincrement=True)
    unique_id = Column(String(255), unique=True, nullable=False)
    course_id = Column(Integer, ForeignKey('course.id'), nullable=False)
    tag_id = Column(String(255), nullable=False)
    ct = Column(DateTime, default=datetime.utcnow)
    ut = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    course = relationship('Course', back_populates='tags')

class CourseTopicMapping(Base):
    __tablename__ = 'course_topic_mapping'
    id = Column(Integer, primary_key=True, autoincrement=True)
    unique_id = Column(String(255), unique=True, nullable=False)
    course_id = Column(Integer, ForeignKey('course.id'), nullable=False)
    topic_id = Column(String(255), nullable=False)
    order = Column(Integer, nullable=False)
    version = Column(Integer, nullable=False)
    ct = Column(DateTime, default=datetime.utcnow)
    ut = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    course = relationship('Course', back_populates='topics')