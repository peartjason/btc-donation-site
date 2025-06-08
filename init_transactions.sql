-- Optional: Create PostgreSQL or SQLite table
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    usd_amount NUMERIC(10, 2),
    btc_amount NUMERIC(18, 8),
    stripe_session_id TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
