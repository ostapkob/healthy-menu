from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import dishes, orders, nutrients
from core.config import settings
from shared.logging import setup_logging, LoggingMiddleware

app = FastAPI(title="Order Service")

# Настройка логирования
setup_logging()

app.add_middleware(LoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
       "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:80",
        "http://localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dishes.router, prefix=settings.API_PREFIX)
app.include_router(orders.router, prefix=settings.API_PREFIX)
app.include_router(nutrients.router, prefix=settings.API_PREFIX)


@app.get("/health")
def health_check():
    return {"status": "ok"}
