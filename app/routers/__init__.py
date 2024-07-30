from app.routers.auth import router as auth_router  # 절대 경로 사용
from app.routers.image import router as image_router  # 절대 경로 사용

__all__ = ["auth_router", "image_router"]
