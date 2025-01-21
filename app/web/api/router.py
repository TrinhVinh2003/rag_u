
from fastapi.routing import APIRouter

from app.web.api import echo, file_upload, gen_response, monitoring

api_router = APIRouter()
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(gen_response.router,prefix="/generate_text"
                          ,tags = ["gen_text"])
api_router.include_router(file_upload.router,prefix="/upload_data",tags=["upload"])
