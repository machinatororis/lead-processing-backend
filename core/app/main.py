from fastapi import FastAPI

from core.app.api.routes import router


app = FastAPI(
    title="Core Service",
    description=(
        "Service responsible for background lead processing and analytics. "
        "It stores processed leads in PostgreSQL and provides affiliate-scoped analytics."
    ),
    version="0.1.0",
    contact={
        "name": "Lead Processing Backend",
    },
    openapi_tags=[
        {
            "name": "Analytics",
            "description": "Affiliate-scoped lead analytics endpoints.",
        }
    ],
)

app.include_router(router, tags=["Analytics"])