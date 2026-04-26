from fastapi import FastAPI

from landings.app.api.routes import router


app = FastAPI(
    title="Landings Service",
    description=(
        "Service responsible for accepting leads from landing pages. "
        "It validates Bearer JWT token, checks affiliate ownership and "
        "pushes accepted leads to Redis queue."
    ),
    version="0.1.0",
    contact={
        "name": "Lead Processing Backend",
    },
    openapi_tags=[
        {
            "name": "Leads",
            "description": "Lead intake endpoints for landing pages.",
        }
    ],
)

app.include_router(router, tags=["Leads"])