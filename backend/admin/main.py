# uvicorn admin.main:app --reload --port 8002

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import dishes, dish_ingredients, ingredients, nutrients, reports, storage  # type: ignore[reportAttributeAccessIssue]

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


app.include_router(dishes.router)
app.include_router(dish_ingredients.router)
app.include_router(ingredients.router)
app.include_router(nutrients.router)
app.include_router(reports.router)
app.include_router(storage.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}

