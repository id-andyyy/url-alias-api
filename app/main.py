from fastapi import FastAPI

from app.api.routes import main_router

app = FastAPI(
    title="URL Alias Service 🪄",
    description="A simple URL alias service that allows users to create short links for their original URLs.",
    version="0.1.0"
)

app.include_router(main_router)


@app.get("/health", description="Health check endpoint", tags=["Health Check ✅"])
async def health_check():
    return {"status": "ok"}
