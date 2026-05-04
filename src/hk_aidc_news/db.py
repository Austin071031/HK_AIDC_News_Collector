from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


def create_engine_and_sessionmaker(
    database_url: str,
) -> tuple[Engine, sessionmaker[Session]]:
    engine = create_engine(database_url, future=True)
    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        future=True,
    )
    return engine, session_factory
