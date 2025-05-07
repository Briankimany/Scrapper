
from app.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def create_db(db_path='test.db'):
    """
    Initialize sqlite data base if it does not exist

    
    """
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    return  Session ,engine
