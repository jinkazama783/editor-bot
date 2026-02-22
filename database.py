import sqlite3
import os
from datetime import datetime, date
from config import Config


class Database:
    def __init__(self):
        self.db_path = Config.DB_PATH
        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    full_name TEXT,
                    is_premium INTEGER DEFAULT 0,
                    premium_expiry TEXT,
                    daily_count INTEGER DEFAULT 0,
                    last_reset TEXT,
                    total_edits INTEGER DEFAULT 0,
                    joined_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS edits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    edit_type TEXT,
                    filter_name TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    amount REAL,
                    status TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def get_or_create_user(self, user_id: int, username: str = "", full_name: str = "") -> dict:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()

            if not row:
                conn.execute(
                    "INSERT INTO users (user_id, username, full_name, last_reset) VALUES (?, ?, ?, ?)",
                    (user_id, username, full_name, str(date.today()))
                )
                conn.commit()
                row = conn.execute(
                    "SELECT * FROM users WHERE user_id = ?", (user_id,)
                ).fetchone()

            return self._row_to_dict(row)

    def _row_to_dict(self, row) -> dict:
        return {
            "user_id": row[0],
            "username": row[1],
            "full_name": row[2],
            "is_premium": bool(row[3]),
            "premium_expiry": row[4],
            "daily_count": row[5],
            "last_reset": row[6],
            "total_edits": row[7],
            "joined_at": row[8],
        }

    def can_edit(self, user_id: int) -> bool:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT daily_count, last_reset, is_premium, premium_expiry FROM users WHERE user_id = ?",
                (user_id,)
            ).fetchone()

            if not row:
                return True

            daily_count, last_reset, is_premium, premium_expiry = row

            if str(date.today()) != last_reset:
                conn.execute(
                    "UPDATE users SET daily_count = 0, last_reset = ? WHERE user_id = ?",
                    (str(date.today()), user_id)
                )
                conn.commit()
                daily_count = 0

            if is_premium:
                if premium_expiry and datetime.strptime(premium_expiry, "%Y-%m-%d").date() >= date.today():
                    return True

            return daily_count < Config.FREE_DAILY_LIMIT

    def increment_edit_count(self, user_id: int, edit_type: str, filter_name: str = ""):
        with self._get_conn() as conn:
            conn.execute(
                "UPDATE users SET daily_count = daily_count + 1, total_edits = total_edits + 1 WHERE user_id = ?",
                (user_id,)
            )
            conn.execute(
                "INSERT INTO edits (user_id, edit_type, filter_name) VALUES (?, ?, ?)",
                (user_id, edit_type, filter_name)
            )
            conn.commit()

    def get_remaining_edits(self, user_id: int) -> int:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT daily_count, last_reset, is_premium, premium_expiry FROM users WHERE user_id = ?",
                (user_id,)
            ).fetchone()

            if not row:
                return Config.FREE_DAILY_LIMIT

            daily_count, last_reset, is_premium, premium_expiry = row

            if str(date.today()) != last_reset:
                return Config.FREE_DAILY_LIMIT

            if is_premium and premium_expiry:
                if datetime.strptime(premium_expiry, "%Y-%m-%d").date() >= date.today():
                    return Config.PREMIUM_DAILY_LIMIT

            return max(0, Config.FREE_DAILY_LIMIT - daily_count)

    def set_premium(self, user_id: int, days: int = 30):
        from datetime import timedelta
        expiry = (date.today() + timedelta(days=days)).strftime("%Y-%m-%d")
        with self._get_conn() as conn:
            conn.execute(
                "UPDATE users SET is_premium = 1, premium_expiry = ? WHERE user_id = ?",
                (expiry, user_id)
            )
            conn.commit()

    def get_stats(self) -> dict:
        with self._get_conn() as conn:
            total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            premium_users = conn.execute("SELECT COUNT(*) FROM users WHERE is_premium = 1").fetchone()[0]
            total_edits = conn.execute("SELECT SUM(total_edits) FROM users").fetchone()[0] or 0
            today_edits = conn.execute(
                "SELECT COUNT(*) FROM edits WHERE DATE(created_at) = ?", (str(date.today()),)
            ).fetchone()[0]
            return {
                "total_users": total_users,
                "premium_users": premium_users,
                "total_edits": total_edits,
                "today_edits": today_edits,
            }

    def get_all_users(self) -> list:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT user_id FROM users").fetchall()
            return [row[0] for row in rows]
