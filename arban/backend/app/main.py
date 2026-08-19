from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from .config import get_settings, Settings
from .logging import setup_logging, get_logger
from .api.routes_health import router as health_router
from .api.routes_markets import router as markets_router
from .api.routes_opportunities import router as opportunities_router
from .api.routes_arbitrage import router as arbitrage_router
from .db.database import init_db

logger = get_logger(__name__)
settings = get_settings()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    setup_logging()
    
    app = FastAPI(
        title=settings.APP_NAME,
        description="Cross-Market Prediction Arbitrage Scanner",
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(health_router, prefix="", tags=["Health"])
    app.include_router(markets_router, prefix="/api/v1", tags=["Markets"])
    app.include_router(opportunities_router, prefix="/api/v1", tags=["Opportunities"])
    app.include_router(arbitrage_router, prefix="/api/v1", tags=["Arbitrage"])
    
    # Startup event
    @app.on_event("startup")
    async def startup():
        logger.info("Starting up ARBAN...")
        await init_db()
        logger.info("Database initialized")
    
    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown():
        logger.info("Shutting down ARBAN...")
    
    return app


app = create_app()
