# admin/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import dishes, tech, foods

app = FastAPI(title="Admin Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
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

app.include_router(tech.router)
app.include_router(dishes.router)
app.include_router(foods.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}

