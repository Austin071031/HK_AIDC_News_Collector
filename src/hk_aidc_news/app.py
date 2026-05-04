from fastapi import FastAPI

from hk_aidc_news.api.routes.health import router as health_router


def create_app() -> FastAPI:
    # A factory keeps app construction deterministic for tests and future config injection.
    app = FastAPI(title="HK AIDC News Collector")
    app.include_router(health_router)
    return app
