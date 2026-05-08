import asyncio
import logging
from hk_aidc_news.config import Settings
from hk_aidc_news.worker import run_daily_pipeline_task

logging.basicConfig(level=logging.INFO)

async def main():
    settings = Settings()
    await run_daily_pipeline_task(settings)

if __name__ == "__main__":
    asyncio.run(main())
