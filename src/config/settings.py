"""Configuration de l'application avec Pydantic Settings."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration de l'application."""

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True

    # HDFS Configuration
    hdfs_host: str = "localhost"
    hdfs_port: int = 9000
    hdfs_path: str = "/sirene_data"

    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""

    # Spark Configuration
    spark_master: str = "local[*]"
    spark_app_name: str = "sirene-dataviz"

    # Data Paths
    data_raw_path: str = "./data/raw"
    data_processed_path: str = "./data/processed"
    data_aggregated_path: str = "./data/aggregated"
    dataset_csv_path: str = "./dataset/Sirene_merged_with_region.csv"

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Environment
    environment: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def redis_url(self) -> str:
        """Retourne l'URL Redis."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def hdfs_url(self) -> str:
        """Retourne l'URL HDFS."""
        return f"hdfs://{self.hdfs_host}:{self.hdfs_port}{self.hdfs_path}"


@lru_cache()
def get_settings() -> Settings:
    """Retourne les settings (singleton)."""
    return Settings()

