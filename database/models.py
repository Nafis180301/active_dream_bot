"""
Database query models for Active Dream Bot.
All database operations are defined here.
"""
from datetime import datetime
from database.db import get_db


# ============================================================
# USER OPERATIONS
# ============================================================

async def get_user(user_id: int) -> dict | None:
    """Get a user by their Telegram user ID."""
    db = await get_db()
    cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()
    if row:
        return dict(row)
    return None


async def create_user(user_id: int, username: str = None, first_name: str = None, last_name: str = None) -> dict:
    """Create a new user record."""
    db = await get_db()
    await db.execute(
        "INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, status) VALUES (?, ?, ?, ?, 'new')",
        (user_id, username, first_name, last_name)
    )
    await db.commit()
    return await get_user(user_id)


async def update_user_status(user_id: int, status: str, approved_by: int = None) -> bool:
    """Update a user's approval status."""
    db = await get_db()
    if status == "approved":
        await db.execute(
            "UPDATE users SET status = ?, approved_at = ?, approved_by = ? WHERE user_id = ?",
            (status, datetime.now().isoformat(), approved_by, user_id)
        )
    else:
        await db.execute(
            "UPDATE users SET status = ? WHERE user_id = ?",
            (status, user_id)
        )
    await db.commit()
    return True


async def set_user_pending(user_id: int, username: str = None, first_name: str = None, last_name: str = None) -> dict:
    """Set a user's status to pending (requesting access)."""
    db = await get_db()
    await db.execute(
        """INSERT INTO users (user_id, username, first_name, last_name, status) 
           VALUES (?, ?, ?, ?, 'pending')
           ON CONFLICT(user_id) DO UPDATE SET 
               username = COALESCE(?, username),
               first_name = COALESCE(?, first_name),
               last_name = COALESCE(?, last_name),
               status = 'pending'""",
        (user_id, username, first_name, last_name, username, first_name, last_name)
    )
    await db.commit()
    return await get_user(user_id)


async def get_all_users(status: str = None) -> list[dict]:
    """Get all users, optionally filtered by status."""
    db = await get_db()
    if status:
        cursor = await db.execute("SELECT * FROM users WHERE status = ? ORDER BY created_at DESC", (status,))
    else:
        cursor = await db.execute("SELECT * FROM users ORDER BY created_at DESC")
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def get_pending_users() -> list[dict]:
    """Get all users with pending status."""
    return await get_all_users("pending")


async def get_approved_users() -> list[dict]:
    """Get all approved users."""
    return await get_all_users("approved")


async def get_user_count() -> dict:
    """Get count of users by status."""
    db = await get_db()
    cursor = await db.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved,
            SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected,
            SUM(CASE WHEN status = 'banned' THEN 1 ELSE 0 END) as banned
        FROM users
    """)
    row = await cursor.fetchone()
    return dict(row) if row else {}


# ============================================================
# BALANCE OPERATIONS
# ============================================================

async def get_balance(user_id: int) -> float:
    """Get a user's current balance."""
    user = await get_user(user_id)
    return user["balance"] if user else 0.0


async def add_balance(user_id: int, amount: float, tx_type: str = "admin_add", description: str = "") -> float:
    """Add balance to a user's account."""
    db = await get_db()
    await db.execute(
        "UPDATE users SET balance = balance + ? WHERE user_id = ?",
        (amount, user_id)
    )
    await db.execute(
        "INSERT INTO transactions (user_id, amount, type, description) VALUES (?, ?, ?, ?)",
        (user_id, amount, tx_type, description)
    )
    await db.commit()
    return await get_balance(user_id)


async def deduct_balance(user_id: int, amount: float, description: str = "") -> float | None:
    """Deduct balance from a user's account. Returns None if insufficient."""
    current = await get_balance(user_id)
    if current < amount:
        return None
    return await add_balance(user_id, -amount, "purchase", description)


async def get_transactions(user_id: int, limit: int = 10) -> list[dict]:
    """Get recent transactions for a user."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM transactions WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit)
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


# ============================================================
# NUMBER OPERATIONS
# ============================================================

async def create_number_record(
    user_id: int, phone_number: str, country: str, country_code: str,
    service: str, order_id: str, cost: float = 0.0
) -> int:
    """Create a number record and return its ID."""
    db = await get_db()
    cursor = await db.execute(
        """INSERT INTO numbers (user_id, phone_number, country, country_code, service, order_id, status, cost)
           VALUES (?, ?, ?, ?, ?, ?, 'waiting', ?)""",
        (user_id, phone_number, country, country_code, service, order_id, cost)
    )
    await db.commit()
    return cursor.lastrowid


async def update_number_status(number_id: int, status: str, sms_code: str = None, sms_full: str = None) -> bool:
    """Update a number record's status."""
    db = await get_db()
    if sms_code:
        await db.execute(
            "UPDATE numbers SET status = ?, sms_code = ?, sms_full = ?, completed_at = ? WHERE id = ?",
            (status, sms_code, sms_full, datetime.now().isoformat(), number_id)
        )
    else:
        await db.execute(
            "UPDATE numbers SET status = ?, completed_at = ? WHERE id = ?",
            (status, datetime.now().isoformat() if status != "waiting" else None, number_id)
        )
    await db.commit()
    return True


async def get_active_numbers(user_id: int) -> list[dict]:
    """Get all active/waiting numbers for a user."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM numbers WHERE user_id = ? AND status IN ('active', 'waiting') ORDER BY created_at DESC",
        (user_id,)
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def get_number_by_id(number_id: int) -> dict | None:
    """Get a number record by its ID."""
    db = await get_db()
    cursor = await db.execute("SELECT * FROM numbers WHERE id = ?", (number_id,))
    row = await cursor.fetchone()
    return dict(row) if row else None


async def get_number_by_order_id(order_id: str) -> dict | None:
    """Get a number record by its 5sim order ID."""
    db = await get_db()
    cursor = await db.execute("SELECT * FROM numbers WHERE order_id = ?", (order_id,))
    row = await cursor.fetchone()
    return dict(row) if row else None


async def get_number_stats() -> dict:
    """Get statistics about numbers."""
    db = await get_db()
    cursor = await db.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN status IN ('active', 'waiting') THEN 1 ELSE 0 END) as active,
            SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled
        FROM numbers
    """)
    row = await cursor.fetchone()
    return dict(row) if row else {}


async def get_user_number_history(user_id: int, limit: int = 10) -> list[dict]:
    """Get number history for a user."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM numbers WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit)
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]
