from fastapi import FastAPI

from core.app.api.routes import router


app = FastAPI(
    title="Core Service",
    description="Service for lead processing and analytics",
    version="0.1.0",
)

app.include_router(router)