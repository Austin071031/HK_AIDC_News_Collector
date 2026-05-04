from fastapi import FastAPI

from hk_aidc_news.api.routes.clusters import router as cluster_router
from hk_aidc_news.api.routes.health import router as health_router


def create_app() -> FastAPI:
    # A factory keeps app construction deterministic for tests and future config injection.
    app = FastAPI(title="HK AIDC News Collector")
    app.include_router(health_router)
    app.include_router(cluster_router)
    return app
