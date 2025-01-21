import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import UJSONResponse
from fastapi.staticfiles import StaticFiles

from app.config.logger_setup import LoggerSetup
from app.core.settings import settings
from app.utils.log_utils import configure_logging
from app.web.api.router import api_router
from app.web.lifespan import lifespan_setup

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # Lấy thư mục gốc của dự án  # noqa: PTH120
LOGGING_CONFIG_PATH = os.path.join(BASE_DIR, "config", "logging_config.yaml")  # noqa: PTH118
LoggerSetup.setup_logging(config_path=LOGGING_CONFIG_PATH)

# Khởi tạo logger
logger = logging.getLogger("app")

def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    configure_logging()
    app = FastAPI(
        title=settings.title,
        version=settings.version,
        description=settings.description,
        lifespan=lifespan_setup,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
        servers=[
            {
                "url": settings.domain,
                "description": "Deployed server",
            },
        ],
    )

    # Main router for the API.
    app.include_router(router=api_router, prefix="/api")

    # Add CORS middleware to allow cross-origin requests
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "*",
        ],  # Allow all origins; replace "*" with specific domains in production
        allow_credentials=True,  # Allow credentials like cookies or headers
        allow_methods=["*"],  # Allow all HTTP methods (GET, POST, OPTIONS, etc.)
        allow_headers=["*"],  # Allow all headers
        expose_headers=["*"],  # Allow specific headers to be exposed
    )

    # Mount some static files
    app.mount(
        "/static/media",
        StaticFiles(directory=settings.media_dir_static),
        name="media",
    )
    return app
app = get_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)  # noqa: S104
