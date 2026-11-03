"""PostgreSQL tests run in isolated, disposable schemas."""

import os
from uuid import uuid4

import psycopg
from psycopg import sql
import pytest


@pytest.fixture
def database():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set TEST_DATABASE_URL to run PostgreSQL integration tests")
    schema = "test_" + uuid4().hex
    with psycopg.connect(url, autocommit=True, connect_timeout=5) as connection:
        connection.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
        try:
            connection.execute(
                sql.SQL("SET search_path TO {}").format(sql.Identifier(schema))
            )
            yield connection
        finally:
            connection.execute(
                sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema))
            )
