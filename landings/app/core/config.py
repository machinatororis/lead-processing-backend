from pydantic_settings import BaseSettings, SettingsConfigDict


class LandingsSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    redis_url: str
    redis_leads_queue: str = "leads_queue"

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"


settings = LandingsSettings()