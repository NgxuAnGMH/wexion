from pydantic_settings import BaseSettings
from pydantic import BaseModel
from typing import Literal
import yaml
from pathlib import Path

class AdminConfig(BaseModel):
    username: str
    password: str

class JWTConfig(BaseModel):
    secret_key: str
    algorithm: Literal["HS256"]
    expire_minutes: int

class DatabaseConfig(BaseModel):
    url: str

class Settings(BaseModel):
    admin: AdminConfig
    jwt: JWTConfig
    database: DatabaseConfig

def load_config() -> Settings:
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)
    return Settings(**config_data)

settings = load_config()
