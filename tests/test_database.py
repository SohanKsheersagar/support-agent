"""Integration tests use a disposable schema, never the development tables."""

import os
from decimal import Decimal
from uuid import uuid4

import psycopg
from psycopg import sql
import pytest

from app.db.migrate import migrate
from app.mock.seed import seed


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


def test_migrate_and_seed_are_repeatable(database):
    migrate(database)
    seed(database)
    database.execute("UPDATE customers SET name = 'Reviewed name' WHERE id = 'C-001'")
    migrate(database)
    seed(database)
    assert database.execute("SELECT count(*) FROM schema_migrations").fetchone() == (1,)
    assert database.execute("SELECT count(*) FROM customers").fetchone() == (6,)
    assert database.execute("SELECT count(*) FROM orders").fetchone() == (8,)
    assert database.execute("SELECT count(*) FROM order_items").fetchone() == (9,)
    assert database.execute("SELECT name FROM customers WHERE id = 'C-001'").fetchone() == (
        "Reviewed name",
    )
    assert database.execute("""
        SELECT c.email, i.sku, i.price, i.qty, o.total
        FROM orders o
        JOIN customers c ON c.id = o.customer_id
        JOIN order_items i ON i.order_id = o.id
        WHERE o.id = 'TH-10482'
    """).fetchone() == (
        "jordan.lee@example.com", "BAG-45L-TRK", Decimal("179.00"), 1, Decimal("179.00")
    )


def test_constraints_reject_invalid_data(database):
    migrate(database)
    seed(database)
    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        database.execute("UPDATE orders SET customer_id = 'missing' WHERE id = 'TH-10482'")
    with pytest.raises(psycopg.errors.CheckViolation):
        database.execute("UPDATE order_items SET qty = 0 WHERE id = 'I-10482-1'")
    with pytest.raises(psycopg.errors.CheckViolation):
        database.execute("UPDATE order_items SET price = -1 WHERE id = 'I-10482-1'")


def test_seed_failure_rolls_back_partial_inserts(database):
    migrate(database)
    database.execute("ALTER TABLE orders ADD CONSTRAINT reject_seed CHECK (total < 0)")
    with pytest.raises(psycopg.errors.CheckViolation):
        seed(database)
    assert database.execute("SELECT count(*) FROM customers").fetchone() == (0,)
