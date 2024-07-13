from pharma_gyan_proj.orm_models.base_model import *

class Course(Base):
    __tablename__ = 'course'
    __table_args__ = {'extend_existing': True}
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

class EntityTag(Base):
    __tablename__ = 'entity_tag'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    unique_id = Column(String(255), unique=True, nullable=False)
    client_id = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    tag_category_id = Column(String(255), nullable=False)
    created_by = Column(String(64))
    is_active = Column(Boolean, default=False)
    ct = Column(DateTime, default=datetime.utcnow)
    ut = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CourseTagMapping(Base):
    __tablename__ = 'course_tag_mapping'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    unique_id = Column(String(255), unique=True, nullable=False)
    course_id = Column(String(255), ForeignKey('course.unique_id'), nullable=False)
    tag_id = Column(String(255), ForeignKey('entity_tag.unique_id'), nullable=False)
    ct = Column(DateTime, default=datetime.utcnow)
    ut = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    course = relationship('Course', back_populates='tags')

    def to_dict(self):
        return {
            'id': self.id,
            'unique_id': self.unique_id,
            'course_id': self.course_id,
            'tag_id': self.tag_id
        }

class CourseTopicMapping(Base):
    __tablename__ = 'course_topic_mapping'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    unique_id = Column(String(255), unique=True, nullable=False)
    course_id = Column(String(255), ForeignKey('course.unique_id'), nullable=False)
    topic_id = Column(String(255), nullable=False)
    order = Column(Integer, nullable=False)
    version = Column(Integer, nullable=False)
    ct = Column(DateTime, default=datetime.utcnow)
    ut = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    course = relationship('Course', back_populates='topics')

    def to_dict(self):
        return {
            'id': self.id,
            'unique_id': self.unique_id,
            'course_id': self.course_id,
            'topic_id': self.topic_id,
            'order': self.order,
            'version': self.version
        }