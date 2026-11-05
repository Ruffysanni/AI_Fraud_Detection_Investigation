"""Create the PostgreSQL tables for fraud assessments and alerts."""

from backend.app.database import get_db_connection


def initialize_database():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id BIGSERIAL PRIMARY KEY,
                    step INTEGER NOT NULL CHECK (step >= 0),
                    transaction_type VARCHAR(20) NOT NULL,
                    amount NUMERIC(18, 2) NOT NULL CHECK (amount >= 0),
                    oldbalance_org NUMERIC(18, 2) NOT NULL,
                    newbalance_orig NUMERIC(18, 2) NOT NULL,
                    oldbalance_dest NUMERIC(18, 2) NOT NULL,
                    newbalance_dest NUMERIC(18, 2) NOT NULL,
                    fraud_score DOUBLE PRECISION NOT NULL
                        CHECK (fraud_score >= 0 AND fraud_score <= 1),
                    prediction INTEGER NOT NULL CHECK (prediction IN (0, 1)),
                    prediction_label VARCHAR(40) NOT NULL,
                    risk_level VARCHAR(10) NOT NULL
                        CHECK (risk_level IN ('low', 'medium', 'high')),
                    threshold DOUBLE PRECISION NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS investigation_alerts (
                    alert_id BIGSERIAL PRIMARY KEY,
                    transaction_id BIGINT NOT NULL UNIQUE
                        REFERENCES transactions(transaction_id)
                        ON DELETE CASCADE,
                    severity VARCHAR(10) NOT NULL
                        CHECK (severity IN ('medium', 'high')),
                    reason TEXT NOT NULL,
                    status VARCHAR(20) NOT NULL DEFAULT 'open'
                        CHECK (status IN ('open', 'reviewed', 'closed')),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS investigation_findings (
                    finding_id BIGSERIAL PRIMARY KEY,
                    transaction_id BIGINT NOT NULL
                        REFERENCES transactions(transaction_id)
                        ON DELETE CASCADE,
                    findings JSONB NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_transactions_created_at
                ON transactions (created_at DESC);
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_alerts_status
                ON investigation_alerts (status);
            """)

    print("Database tables created or already exist successfully.")


if __name__ == "__main__":
    initialize_database()
