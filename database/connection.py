from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

URL = os.getenv("DATABASE_PUBLIC_URL")

# Configuração do SQLAlchemy
engine = create_engine(URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
