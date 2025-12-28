import os
from typing import Optional

class Settings:
    def __init__(self):
        self.database_url: Optional[str] = os.getenv("DATABASE_URL")
        self.webhook_secret: Optional[str] = os.getenv("WEBHOOK_SECRET")
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")

        if not self.database_url:
            raise RuntimeError("DATABASE_URL is not set")

        if not self.webhook_secret:
            raise RuntimeError("WEBHOOK_SECRET is not set")


settings = Settings()