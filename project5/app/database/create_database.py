from sqlalchemy import create_engine
from schema import Base

engine = create_engine('sqlite:///startup.db')
Base.metadata.drop_all(engine, checkfirst=True)
Base.metadata.create_all(engine)
