from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
  mariadb_user: str = "root"
  mariadb_password: str = "1234"
  mariadb_host: str = "192.168.0.204"
  mariadb_database: str = "edu"
  mariadb_port: int = "3306"

  model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    extra="ignore"
  )

settings = Settings()
