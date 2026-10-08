"""
ClaimGraph AI — Config / Settings tests.
"""

from __future__ import annotations

from app.core.config import Settings, get_settings


def test_settings_loads_defaults() -> None:
    """Settings should load with sane defaults without a .env file."""
    settings = get_settings()
    assert settings.app_name == "ClaimGraph AI"
    assert settings.app_env == "development"
    assert settings.app_port == 8000


def test_database_url_property() -> None:
    """database_url should compose a valid async PG connection string."""
    settings = Settings()
    url = settings.database_url
    assert url.startswith("postgresql+asyncpg://")
    assert settings.postgres_db in url


def test_cors_origin_list() -> None:
    """CORS origins should be parsed into a list."""
    settings = Settings(cors_origins="http://a.com, http://b.com")
    origins = settings.cors_origin_list
    assert len(origins) == 2
    assert "http://a.com" in origins
    assert "http://b.com" in origins


def test_redis_url_without_password() -> None:
    """Redis URL without a password should omit the auth segment."""
    settings = Settings(redis_password="")
    assert ":@" not in settings.redis_url


def test_redis_url_with_password() -> None:
    """Redis URL with a password should include the auth segment."""
    settings = Settings(redis_password="secret123")
    assert ":secret123@" in settings.redis_url
