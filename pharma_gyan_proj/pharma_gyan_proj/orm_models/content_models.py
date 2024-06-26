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

    units = relationship("PgUnit", backref="subject", cascade="all, delete-orphan")

    def __init__(self, data={}):
        Orm_helper.__init__(self, data)

    def to_dict(self):
        return {
            "id": self.id,
            "unique_id": self.unique_id,
            "title": self.name,
            "description": self.description,
            "topics": [unit.to_dict() for unit in self.units]
        }

class PgUnit(Base, Orm_helper):
    __tablename__ = 'unit'

    id = Column("id", Integer, autoincrement=True, primary_key=True)
    unique_id = Column("unique_id", String, primary_key=True)
    title = Column("title", String)
    subject_id = Column("subject_id", Integer, ForeignKey('subject.unique_id'))
    created_by = Column("created_by", String)
    ct = Column("ct", DateTime, default=datetime.utcnow)

    chapters = relationship("PgChapter", backref="unit", cascade="all, delete-orphan")

    def __init__(self, data={}):
        Orm_helper.__init__(self, data)

    def to_dict(self):
        return {
            "id": self.id,
            "unique_id": self.unique_id,
            "title": self.title,
        }

class PgChapter(Base, Orm_helper):
    __tablename__ = 'chapter'

    id = Column("id", Integer, autoincrement=True, primary_key=True)
    unique_id = Column("unique_id", String, primary_key=True)
    title = Column("title", String)
    content = Column("content", Text)
    unit_id = Column("unit_id", Integer, ForeignKey('unit.unique_id'))
    created_by = Column("created_by", String)
    ct = Column("ct", DateTime, default=datetime.utcnow)

    def __init__(self, data={}):
        Orm_helper.__init__(self, data)

    def to_dict(self):
        return {
            "id": self.id,
            "unique_id": self.unique_id,
            "title": self.title,
            "content": self.content,
            "unit_id": self.unit_id,
            "created_by": self.created_by,
            "ct": self.ct.isoformat() if self.ct else None
        }
