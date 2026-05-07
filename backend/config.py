from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///jinwen_daily.db"
    serverless_mode: bool = False  # 设为 True 时数据库存 /tmp/（兼容阿里云函数计算）
    admin_key: str = "jinwen-admin-2026"

    # AI API
    ai_key: str = ""
    ai_url: str = "https://api.openai.com/v1"
    ai_model: str = "gpt-4o-mini"

    # Crawler settings
    crawl_hour: int = 2  # 凌晨2点
    crawl_minute: int = 0
    days_back: int = 3  # 回溯天数

    app_name: str = "金文日报 API"
    app_version: str = "1.0.0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
