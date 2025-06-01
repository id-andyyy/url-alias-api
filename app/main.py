from fastapi import FastAPI

from app.api.routes import main_router

app = FastAPI(
    title="URL Alias Service",
    description="Сервис для создания коротких URL-адресов",
    version="0.1.0"
)

app.include_router(main_router)


@app.get("/health", description="Проверка работоспособности сервисa")
async def health_check():
    return {"status": "ok"}
