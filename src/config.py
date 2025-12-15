from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ntfy_base_url: str = "https://ntfy.sh"
    asset_price_url: str = "https://api.stonks.com/api/v3/simple/price"
    check_interval_seconds: int = 30
    database_url: str = "sqlite:///alerts.db"
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings()
