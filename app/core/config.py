from pydantic import BaseSettings

class Settings(BaseSettings):
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    database_url: str

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
