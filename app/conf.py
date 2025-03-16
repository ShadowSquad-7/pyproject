from pydantic_settings import BaseSettings
from pydantic import model_validator

class Settings(BaseSettings):
    HOST: str
    PORT: int
    NAME_DB: str
    USER_DB: str
    PASS: str
    DATABASE_URL: str = ""

    @model_validator(mode="after")
    def assemble_db_url(self) -> "Settings":
        
        self.DATABASE_URL = f"postgresql+asyncpg://{self.USER_DB}:{self.PASS}@{self.HOST}:{self.PORT}/{self.NAME_DB}"
        return self

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }

settings = Settings()