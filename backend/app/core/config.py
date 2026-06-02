from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    app_secret_key: str
    fernet_key: str
    firefly_base_url: str
    firefly_access_token: str
    app_env: str = "development"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
