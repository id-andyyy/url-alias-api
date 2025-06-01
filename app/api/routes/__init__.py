from fastapi import APIRouter

from app.api.routes.links import router as links_router
from app.api.routes.stats import router as stats_router
from app.api.routes.public import router as public_router

main_router = APIRouter()
main_router.include_router(links_router, prefix="/api/links", tags=["Links 🔗"])
main_router.include_router(stats_router, prefix="/api/stats", tags=["Stats 📊"])
main_router.include_router(public_router, tags=["Public 🧭"])
