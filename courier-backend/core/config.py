import os
from functools import lru_cache


class Settings:
    API_PREFIX: str = "/api/v1/courier"
    TOPIC: str = "new_orders"
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

