from pharma_gyan_proj.orm_models.base_model import *
from pharma_gyan_proj.utils.common_utils import url_to_base64

Base = declarative_base()
import json

Base = declarative_base()

class Orm_helper:
    def __init__(self, data={}):
        for key, value in data.items():
            setattr(self, key, value)

class PgCourse(Base, Orm_helper):
    __tablename__ = 'course'

    id = Column("id", Integer, autoincrement=True, primary_key=True)
    unique_id = Column("unique_id", String, primary_key=True)
    title = Column("title", String)
    description = Column("description", Text)
    price = Column("price", Numeric(10, 2))
    thumbnail_url = Column("thumbnail_url", String)
    created_by = Column("created_by", String)
    is_active = Column("is_active", Integer, default=1)
    ct = Column("ct", DateTime, default=datetime.utcnow)

    semesters = relationship("PgSemester", backref="course", cascade="all, delete-orphan")

    def __init__(self, data={}):
        Orm_helper.__init__(self, data)

    def to_dict(self):
        return {
            "id": self.id,
            "unique_id": self.unique_id,
            "courseTitle": self.title,
            "courseDescription": self.description,
            "coursePrice": str(self.price),
            "courseImage": url_to_base64(self.thumbnail_url),
            "semesters": [semester.to_dict() for semester in self.semesters]
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)

class PgSemester(Base, Orm_helper):
    __tablename__ = 'semester'

    id = Column("id", Integer, autoincrement=True, primary_key=True)
    unique_id = Column("unique_id", String, primary_key=True)
    title = Column("title", String)
    course_id = Column("course_id", String, ForeignKey('course.unique_id'))
    created_by = Column("created_by", String)
    ct = Column("ct", DateTime, default=datetime.utcnow)

    subjects = relationship("PgSubject", backref="semester", cascade="all, delete-orphan")

    def __init__(self, data={}):
        Orm_helper.__init__(self, data)

    def to_dict(self):
        return {
            "id": self.id,
            "unique_id": self.unique_id,
            "semesterId": int(self.title),
            "subjects": [subject.to_dict() for subject in self.subjects]
        }

class PgSubject(Base, Orm_helper):
    __tablename__ = 'subject'

    id = Column("id", Integer, autoincrement=True, primary_key=True)
    unique_id = Column("unique_id", String, primary_key=True)
    name = Column("name", String)
    description = Column("description", Text)
    semester_id = Column("semester_id", Integer, ForeignKey('semester.unique_id'))
    created_by = Column("created_by", String)
    ct = Column("ct", DateTime, default=datetime.utcnow)


    def __init__(self, data={}):
        Orm_helper.__init__(self, data)

    def to_dict(self):
        return {
            "id": self.id,
            "unique_id": self.unique_id,
            "title": self.name,
            "description": self.description
        }

class PgTopic(Base, Orm_helper):
    __tablename__ = 'topic'

    id = Column("id", Integer, autoincrement=True, primary_key=True)
    unique_id = Column("unique_id", String)
    client_id = Column("client_id", String)
    title = Column("title", String)
    description = Column("description", String)
    version = Column("version", Integer)
    is_active = Column("is_active", Integer, default='0')
    created_by = Column("created_by", String)
    ct = Column("ct", DateTime, default=datetime.utcnow)
    ut = Column("ut", TIMESTAMP,
                server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __init__(self, data={}):
        Orm_helper.__init__(self, data)

    def to_dict(self):
        return {
            "id": self.id,
            "unique_id": self.unique_id,
            "title": self.title,
            "chapters": [chapter.to_dict() for chapter in self.chapters]
        }
    
    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)

class PgChapter(Base, Orm_helper):
    __tablename__ = 'chapter'

    id = Column("id", Integer, autoincrement=True, primary_key=True)
    unique_id = Column("unique_id", String, primary_key=True)
    title = Column("title", String)
    content = Column("content", Text)
    index = Column("index", Integer)
    unit_id = Column("unit_id", Integer, ForeignKey('unit.unique_id'))
    created_by = Column("created_by", String)
    mark_as_free = Column("mark_as_free", Integer, default=0)
    ct = Column("ct", DateTime, default=datetime.utcnow)

    def __init__(self, data={}):
        Orm_helper.__init__(self, data)

    def to_dict(self):
        return {
            "id": self.id,
            "unique_id": self.unique_id,
            "title": self.title,
            "content": self.content,
            "index": self.index,
            "unit_id": self.unit_id,
            "created_by": self.created_by,
            "mark_as_free":self.mark_as_free,
            "ct": self.ct.isoformat() if self.ct else None
        }
