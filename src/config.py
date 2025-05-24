from pathlib import Path
from pydantic import SecretStr, Field, PostgresDsn, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    db_host: str = Field(..., env="DB_HOST")
    db_port: int = Field(..., env="DB_PORT")
    db_user: str = Field(..., env="DB_USER")
    db_pass: SecretStr = Field(..., env="DB_PASS")
    db_name: str = Field(..., env="DB_NAME")

    secret_key: SecretStr = Field(..., env="SECRET_KEY")
    algorithm: str = Field("HS256", env="ALGORITHM")
    prometheus_url: str = Field(..., env="PROMETHEUS_URL")

    @property
    def db_url(self) -> PostgresDsn:
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.db_user,
                password=self.db_pass.get_secret_value(),
                host=self.db_host,
                port=self.db_port,
                path=f"{self.db_name}",
            )
        )


settings = Settings()
