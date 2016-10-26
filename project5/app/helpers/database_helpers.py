from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from schema import Base


def create_session(database):
    engine = create_engine(database)
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    return DBSession()
