from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./app.db"
    db_pool_size: int = 20
    db_max_overflow: int = 10
    db_pool_recycle: int = 1800
    jwt_secret_key: str = "CHANGE_ME_IN_PRODUCTION"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    environment: str = "development"
    
    IMAGEKIT_PUBLIC_KEY: str = ""
    IMAGEKIT_PRIVATE_KEY: str = ""
    IMAGEKIT_URL_ENDPOINT: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()