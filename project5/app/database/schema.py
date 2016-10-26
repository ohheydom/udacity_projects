from sqlalchemy import (Column, ForeignKey, Integer, String, DateTime,
                        UniqueConstraint)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(30), nullable=False)
    email = Column(String(40), nullable=False)
    created = Column(DateTime(timezone=True), server_default=func.now())


class City(Base):
    __tablename__ = 'city'
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    state = Column(String(30), nullable=False)
    slug = Column(String(30), nullable=False)
    startups = relationship('Startup')

    def serialize(self):
        l = []
        for startup in self.startups:
            d = {}
            d['id'] = startup.id
            d['name'] = startup.name
            d['slug'] = startup.slug
            d['description'] = startup.description
            d['link'] = startup.link
            d['careers_link'] = startup.careers_link
            d['user_id'] = startup.user_id
            d['created'] = startup.created
            l.append(d)

        return {'id': self.id,
                'name': self.name,
                'state': self.state,
                'slug': self.slug,
                'startups': l
                }


class Startup(Base):
    __tablename__ = 'startup'
    id = Column(Integer, primary_key=True)
    name = Column(String(40), nullable=False)
    slug = Column(String(40), nullable=False)
    description = Column(String(500))
    link = Column(String(100))
    careers_link = Column(String(100))
    city_id = Column(Integer, ForeignKey('city.id'))
    city = relationship(City)
    created = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), server_default=func.now(),
                          onupdate=func.current_timestamp())
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User')

    __table_args__ = (UniqueConstraint('name', 'city_id'),)

    def serialize(self):
        d = {}
        d['id'] = self.id
        d['name'] = self.name
        d['slug'] = self.slug
        d['description'] = self.description
        d['link'] = self.link
        d['careers_link'] = self.careers_link
        d['user_id'] = self.user_id
        d['created'] = self.created
        return d
