import json
from pharma_gyan_proj.orm_models.base_model import *
from pharma_gyan_proj.utils.common_utils import url_to_base64

class Course(Base):
    __tablename__ = 'course'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    unique_id = Column(String(255), nullable=False)
    client_id = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    created_by = Column(String(64))
    is_active = Column(Boolean, default=False)
    version = Column(Integer, nullable=False)
    ct = Column(DateTime, default=datetime.utcnow)
    ut = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tags = relationship('CourseTagMapping', back_populates='course', cascade='all, delete, delete-orphan')
    topics = relationship('CourseTopicMapping', back_populates='course', cascade='all, delete, delete-orphan', order_by='CourseTopicMapping.order')

    def to_dict(self):
        return {
            "id": self.id,
            "unique_id": self.unique_id,
            "title": self.title,
            "description": self.description,
            "tags": [tag.tag_id for tag in self.tags],
            "topics": [topic.topic_id for topic in self.topics]
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)

class CourseTagMapping(Base):
    __tablename__ = 'course_tag_mapping'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    unique_id = Column(String(255), unique=True, nullable=False)
    course_id = Column(String(255), ForeignKey('course.id'), nullable=False)
    tag_id = Column(String(255), nullable=False)
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
    course_id = Column(String(255), ForeignKey('course.id'), nullable=False)
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
    
class Package(Base):
    __tablename__ = 'package'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    unique_id = Column(String(255), nullable=False)
    client_id = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    thumbnail_url = Column(String(255))
    created_by = Column(String(64))
    is_active = Column(Boolean, default=False)
    version = Column(Integer, nullable=False)
    ct = Column(DateTime, default=datetime.utcnow)
    ut = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    courses = relationship('PackageCourseMapping', back_populates='package', cascade='all, delete, delete-orphan')

    def to_dict(self):
        return {
            "id": self.id,
            "unique_id": self.unique_id,
            "client_id": self.client_id,
            "title": self.title,
            "description": self.description,
            "price": float(self.price),
            "thumbnail_url": url_to_base64(self.thumbnail_url),
            "is_active": self.is_active,
            "version": self.version,
            "courses": [course.course_id for course in self.courses]
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)

class PackageCourseMapping(Base):
    __tablename__ = 'package_course_mapping'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    unique_id = Column(String(255), unique=True, nullable=False)
    course_id = Column(String(255), nullable=False)
    package_id = Column(Integer, ForeignKey('package.id'), nullable=False)
    version = Column(Integer, nullable=False)
    ct = Column(DateTime, default=datetime.utcnow)
    ut = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    package = relationship('Package', back_populates='courses')

    def to_dict(self):
        return {
            'id': self.id,
            'unique_id': self.unique_id,
            'course_id': self.course_id,
            'package_id': self.package_id,
            'version': self.version
        }