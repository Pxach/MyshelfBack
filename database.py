from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decouple import config

db_url=config('db_url').replace("://", "ql://", 1)

engine=create_engine(db_url, echo=True)
Base=declarative_base()
SessionLocal=sessionmaker(bind=engine)

