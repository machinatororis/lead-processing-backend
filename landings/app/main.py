from fastapi import FastAPI

from landings.app.api.routes import router


app = FastAPI(
    title="Landings Service",
    description="Service for accepting leads from landing pages",
    version="0.1.0",
)

app.include_router(router)