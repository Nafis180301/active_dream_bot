"""
Database connection and initialization for Active Dream Bot.
Uses aiosqlite for async SQLite operations.
"""
import aiosqlite
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "active_dream.db")

_db: aiosqlite.Connection | None = None


async def get_db() -> aiosqlite.Connection:
    """Get the database connection, creating it if necessary."""
    global _db
    if _db is None:
        _db = await aiosqlite.connect(DB_PATH)
        _db.row_factory = aiosqlite.Row
        await _db.execute("PRAGMA journal_mode=WAL")
        await _db.execute("PRAGMA foreign_keys=ON")
    return _db


async def close_db():
    """Close the database connection."""
    global _db
    if _db is not None:
        await _db.close()
        _db = None


async def init_db():
    """Initialize database tables."""
    db = await get_db()

    await db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            status TEXT NOT NULL DEFAULT 'new',
            balance REAL NOT NULL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            approved_at TIMESTAMP,
            approved_by INTEGER,
            CONSTRAINT chk_status CHECK (status IN ('new', 'pending', 'approved', 'rejected', 'banned'))
        );

        CREATE TABLE IF NOT EXISTS numbers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            phone_number TEXT,
            country TEXT,
            country_code TEXT,
            service TEXT,
            order_id TEXT,
            status TEXT NOT NULL DEFAULT 'active',
            sms_code TEXT,
            sms_full TEXT,
            cost REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            CONSTRAINT chk_num_status CHECK (status IN ('active', 'waiting', 'completed', 'cancelled', 'expired', 'error'))
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            CONSTRAINT chk_tx_type CHECK (type IN ('deposit', 'purchase', 'refund', 'admin_add', 'withdrawal'))
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);
        CREATE INDEX IF NOT EXISTS idx_numbers_user ON numbers(user_id);
        CREATE INDEX IF NOT EXISTS idx_numbers_status ON numbers(status);
        CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id);
    """)

    await db.commit()
    print("✅ Database initialized successfully.")
