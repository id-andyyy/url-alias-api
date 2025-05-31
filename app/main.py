from fastapi import FastAPI

app = FastAPI(
    title="URL Alias Service",
    description="Сервис для создания коротких URL-адресов",
    version="0.1.0"
)


@app.get("/health", description="Проверка работоспособности сервисa")
async def health_check():
    return {"status": "ok"}
