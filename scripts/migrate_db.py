import os
import sys

# Ensure src is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from sqlalchemy import text
from hk_aidc_news.db import engine
from hk_aidc_news.models.base import Base

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

if __name__ == "__main__":
    migrate()
