import os
import sys
from pathlib import Path
import yaml

# Ensure src is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from sqlalchemy import text
from hk_aidc_news.db import engine, session_factory
from hk_aidc_news.models.base import Base
from hk_aidc_news.models.source import Source
from hk_aidc_news.models.search_keyword import SearchKeyword

def get_yaml_path() -> Path:
    return Path(__file__).parent.parent / "data" / "sources" / "seed_sources.yaml"

def seed_data(session_maker):
    with session_maker() as db_session:
        # Seed Sources
        if db_session.query(Source).count() == 0:
            yaml_path = get_yaml_path()
            if yaml_path.exists():
                payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
                for item in payload.get("sources", []):
                    source = Source(**item)
                    db_session.add(source)
                db_session.commit()
                print("Seeded sources from yaml.")
        
        # Seed Keywords
        if db_session.query(SearchKeyword).count() == 0:
            default_keyword = SearchKeyword(keyword="Hong Kong AI data center", active=True)
            db_session.add(default_keyword)
            db_session.commit()
            print("Seeded default search keyword.")

def migrate():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE sources ADD COLUMN rss_url VARCHAR(2048);"))
            conn.commit()
            print("Added rss_url to sources.")
        except Exception as e:
            print(f"Column might already exist: {e}")
            conn.rollback()

    Base.metadata.create_all(bind=engine)
    print("Database schema updated.")

    seed_data(session_factory)

if __name__ == "__main__":
    migrate()
