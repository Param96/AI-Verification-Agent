from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Enterprise Verify Platform"
    API_V1_STR: str = "/api/v1"
    
    # PostgreSQL Configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "verify_admin"
    POSTGRES_PASSWORD: str = "secure_password_123"
    POSTGRES_DB: str = "verify_platform"
    POSTGRES_PORT: int = 5432
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Redis / Celery Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # MinIO / S3 Configuration
    MINIO_SERVER: str = "localhost:9000"
    MINIO_ROOT_USER: str = "minio_admin"
    MINIO_ROOT_PASSWORD: str = "minio_secure_password"
    MINIO_SECURE: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
