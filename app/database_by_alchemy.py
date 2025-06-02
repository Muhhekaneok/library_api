from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.db_config import db_config

SQLALCHEMY_DATABASE_URL = (f"postgresql://{db_config['user']}:{db_config['password']}"
                           f"@{db_config['host']}/{db_config['dbname']}")

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
