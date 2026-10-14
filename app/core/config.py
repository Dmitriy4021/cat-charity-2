from typing import Optional

from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_author: str = 'Ваше имя'
    database_url: str = 'sqlite+aiosqlite:///./cat_charity.db'
    path: str
    app_title: str = 'QRKot'
    app_description: str = """В этом приложении будут открываться «целевые
        проекты» — сборы конкретных сумм под конкретную задачу, а пользователи
        будут отправлять пожертвования для сбора требуемых сумм."""

    secret: str = 'SECRET'

    first_superuser_email: Optional[EmailStr] = None
    first_superuser_password: Optional[str] = None

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()
