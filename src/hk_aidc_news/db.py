from typing import Tuple, Generator
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from hk_aidc_news.config import Settings

def create_engine_and_sessionmaker(
    database_url: str,
) -> Tuple[Engine, sessionmaker]:
    engine = create_engine(database_url, future=True)
    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        future=True,
    )
    return engine, session_factory

settings = Settings()
engine, session_factory = create_engine_and_sessionmaker(settings.database_url)

def get_session() -> Generator:
    with session_factory() as session:
        yield session
