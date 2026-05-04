from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from hk_aidc_news.db import create_engine_and_sessionmaker


def test_create_engine_and_sessionmaker() -> None:
    engine, session_factory = create_engine_and_sessionmaker("sqlite+pysqlite:///:memory:")

    assert str(engine.url) == "sqlite+pysqlite:///:memory:"
    assert session_factory is not None


def test_session_factory_keeps_committed_instances_usable() -> None:
    class Base(DeclarativeBase):
        pass

    class Widget(Base):
        __tablename__ = "widgets"

        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str]

    engine, session_factory = create_engine_and_sessionmaker("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with session_factory() as session:
        widget = Widget(name="alpha")
        session.add(widget)
        session.commit()

    assert widget.id is not None
    assert widget.name == "alpha"
