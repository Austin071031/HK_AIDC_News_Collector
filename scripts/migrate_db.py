import os
import sys
from pathlib import Path

# Ensure src is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from sqlalchemy import text
from hk_aidc_news.db import engine, session_factory
from hk_aidc_news.models.base import Base
from hk_aidc_news.models.source import Source
from hk_aidc_news.models.search_keyword import SearchKeyword

def seed_data(session_maker):
    with session_maker() as db_session:
        # Seed Sources
        if db_session.query(Source).count() == 0:
            default_sources = [
                {
                    "name": "Data Center Dynamics APAC",
                    "base_url": "https://www.datacenterdynamics.com",
                    "rss_url": "https://www.datacenterdynamics.com/en/rss/",
                    "region": "southeast_asia",
                    "language": "en",
                    "source_type": "industry_media",
                    "discovery_mode": "rss",
                    "priority": 1,
                    "active": True
                }
            ]
            for item in default_sources:
                source = Source(**item)
                db_session.add(source)
            db_session.commit()
            print("Seeded default sources.")
        
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
