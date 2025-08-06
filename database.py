from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from config import DB_URL

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)
    return Session()