import logging

from pydantic import BaseConfig


class Settings(BaseConfig):
    logger_name = 'vector-search-api'
    logger = logging.getLogger(logger_name)


settings = Settings()
