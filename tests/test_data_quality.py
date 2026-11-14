import os

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()


@pytest.fixture(scope="module")
def conn():
    url = (
        f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
        f"@{os.getenv('DB_HOST')}:3306/{os.getenv('DB_NAME')}"
    )
    with create_engine(url).connect() as c:
        yield c


def scalar(conn, sql):
    return conn.execute(text(sql)).scalar()


def test_transaction_row_count(conn):
    assert scalar(conn, "SELECT COUNT(*) FROM transactions") == 590540


def test_identity_row_count(conn):
    assert scalar(conn, "SELECT COUNT(*) FROM identity") == 144233


def test_no_duplicate_transaction_ids(conn):
    sql = "SELECT COUNT(*) - COUNT(DISTINCT TransactionID) FROM transactions"
    assert scalar(conn, sql) == 0


def test_fraud_label_is_binary(conn):
    sql = "SELECT COUNT(*) FROM transactions WHERE isFraud NOT IN (0, 1)"
    assert scalar(conn, sql) == 0


def test_amount_is_positive(conn):
    assert (
        scalar(conn, "SELECT COUNT(*) FROM transactions WHERE TransactionAmt <= 0") == 0
    )


def test_fraud_rate_is_plausible(conn):
    rate = float(scalar(conn, "SELECT AVG(isFraud) FROM transactions"))
    assert 0.03 < rate < 0.04


def test_identity_links_to_transactions(conn):
    sql = """
        SELECT COUNT(*) FROM identity i
        LEFT JOIN transactions t ON t.TransactionID = i.TransactionID
        WHERE t.TransactionID IS NULL
    """
    assert scalar(conn, sql) == 0
