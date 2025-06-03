from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

from sqlalchemy.exc import IntegrityError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

from app.api.routes import main_router

app = FastAPI(
    title="URL Alias Service 🪄",
    description="A simple URL alias service that allows users to create short links for their original URLs.",
    version="0.1.0"
)


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=400,
        content={"message": f"Database integrity error: {exc.orig}"}
    )


app.include_router(main_router)


@app.get(
    "/api/health",
    description="Health check endpoint.",
    tags=["Health Check 👌"]
)
async def health_check():
    return {"status": "ok"}
