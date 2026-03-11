from app.core.config import normalize_database_url


def test_normalize_postgres_url():
    assert normalize_database_url("postgres://user:pass@host/db") == "postgresql+psycopg://user:pass@host/db"


def test_normalize_postgresql_url():
    assert normalize_database_url("postgresql://user:pass@host/db") == "postgresql+psycopg://user:pass@host/db"


def test_leave_other_urls_unchanged():
    assert normalize_database_url("sqlite:///./app.db") == "sqlite:///./app.db"
