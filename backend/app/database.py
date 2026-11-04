
import os

import psycopg
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    """Create and return a PostgreSQL database connection."""

    password = os.getenv("DB_PASSWORD")

    if not password:
        raise RuntimeError(
            "DB_PASSWORD is not configured. "
            "Check your environment variables."
        )

    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "fraud_investigation_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=password,
    )
