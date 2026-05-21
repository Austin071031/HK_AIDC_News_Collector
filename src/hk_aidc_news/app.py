from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from hk_aidc_news.api.routes.actions import router as actions_router
from hk_aidc_news.api.routes.articles import router as articles_router
from hk_aidc_news.api.routes.clusters import router as cluster_router
from hk_aidc_news.api.routes.health import router as health_router
from hk_aidc_news.api.routes.jobs import router as jobs_router
from hk_aidc_news.api.routes.keywords import router as keywords_router
from hk_aidc_news.api.routes.sources import router as sources_router
from hk_aidc_news.api.routes.config import router as config_router


def create_app() -> FastAPI:
    # A factory keeps app construction deterministic for tests and future config injection.
    app = FastAPI(title="HK AIDC News Collector")
    
    # Add CORS middleware to allow Next.js frontend calls
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(cluster_router)
    app.include_router(actions_router)
    app.include_router(articles_router)
    app.include_router(jobs_router)
    app.include_router(keywords_router)
    app.include_router(sources_router)
    app.include_router(config_router)
    return app
