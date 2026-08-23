from fastapi import FastAPI

from app.api.routes import health, recommendations
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="Crypto Portfolio Agent",
        version="0.1.0",
        description="AI-assisted crypto portfolio recommendation API.",
    )
    app.include_router(health.router)
    app.include_router(recommendations.router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
