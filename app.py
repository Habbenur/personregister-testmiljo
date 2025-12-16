#!/usr/bin/env python3
"""
Personregister i testmiljö – GDPR-anpassad testdata med Faker

- Skapar testdata (name/email/personnummer/address) med Faker
- Anonymiserar fälten (email/personnummer/address/name)
- Kontrollerar vid varje körning och dagligen att testdata är anonymiserad
- Enhetstester: python app.py --test
"""

from __future__ import annotations

import argparse
import cmd
import datetime as dt
import hashlib
import os
import re
import sqlite3
import sys
import tempfile
import unittest
from dataclasses import dataclass
from typing import Optional, Tuple

from faker import Faker


# -----------------------------
# Config
# -----------------------------
DEFAULT_DB_PATH = os.getenv("DATABASE_PATH", "./test_users.db")
FAKER_LOCALE = os.getenv("FAKER_LOCALE", "sv_SE")

ANON_NAME = "Anonym Användare"
ANON_EMAIL_DOMAIN = "anon.test"
ANON_PERSONNUMMER = "000000-0000"
ANON_ADDRESS = "REDACTED"

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PERSONNUMMER_RE = re.compile(r"^\d{6}-\d{4}$")  # YYMMDD-XXXX


@dataclass(frozen=True)
class UserRow:
    id: int
    name: str
    email: str
    personnummer: str
    address: str
    is_test_data: int
    is_anonymized: int
    created_at: str
    updated_at: str


# -----------------------------
# DB helpers
# -----------------------------
def connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def init_db(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT NOT NULL,
            email           TEXT NOT NULL,
            personnummer    TEXT NOT NULL,
            address         TEXT NOT NULL,
            is_test_data    INTEGER NOT NULL DEFAULT 1,
            is_anonymized   INTEGER NOT NULL DEFAULT 0,
            created_at      TEXT NOT NULL,
            updated_at      TEXT NOT NULL
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS meta (
            key     TEXT PRIMARY KEY,
            value   TEXT NOT NULL
        );
        """
    )

    conn.commit()


def meta_get(conn: sqlite3.Connection, key: str) -> Optional[str]:
    cur = conn.cursor()
    cur.execute("SELECT value FROM meta WHERE key = ?", (key,))
    row = cur.fetchone()
    return None if row is None else row["value"]


def meta_set(conn: sqlite3.Connection, key: str, value: str) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO meta(key, value) VALUES(?, ?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """,
        (key, value),
    )
    conn.commit()


# -----------------------------
# Faker-based data
# -----------------------------
def faker_instance() -> Faker:
    return Faker(FAKER_LOCALE)


def make_personnummer(fake: Faker) -> str:
    # Simple YYMMDD-XXXX format
    d = fake.date_of_birth(minimum_age=18, maximum_age=90)
    yy = d.year % 100
    mm = d.month
    dd = d.day
    xxxx = fake.random_int(min=0, max=9999)
    return f"{yy:02d}{mm:02d}{dd:02d}-{xxxx:04d}"


def seed_raw_test_data(conn: sqlite3.Connection, n: int = 10) -> int:
    fake = faker_instance()
    cur = conn.cursor()
    now = utc_now_iso()

    rows = []
    for _ in range(n):
        name = fake.name()
        email = fake.email()
        if not EMAIL_RE.match(email):
            email = f"{hashlib.sha256(email.encode()).hexdigest()[:10]}@example.com"

        personnummer = make_personnummer(fake)
        address = fake.address().replace("\n", ", ")

        rows.append((name, email, personnummer, address, 1, 0, now, now))

    cur.executemany(
        """
        INSERT INTO users(name, email, personnummer, address, is_test_data, is_anonymized, created_at, updated_at)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()
    return cur.rowcount


# -----------------------------
# Anonymization
# -----------------------------
def stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def anonymize_email(email: str) -> str:
    token = stable_hash(email)[:12]
    return f"{token}@{ANON_EMAIL_DOMAIN}"


def anonymize_personnummer(_: str) -> str:
    return ANON_PERSONNUMMER


def anonymize_address(_: str) -> str:
    return ANON_ADDRESS


def is_row_anonymized(row: UserRow) -> bool:
    return (
        row.name == ANON_NAME
        and row.email.endswith(f"@{ANON_EMAIL_DOMAIN}")
        and row.personnummer == ANON_PERSONNUMMER
        and row.address == ANON_ADDRESS
        and row.is_anonymized == 1
    )


def anonymize_non_anonymized_test_rows(conn: sqlite3.Connection) -> int:
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, name, email, personnummer, address, is_test_data, is_anonymized, created_at, updated_at
        FROM users
        WHERE is_test_data = 1
        """
    )
    rows = [UserRow(**dict(r)) for r in cur.fetchall()]

    now = utc_now_iso()
    updated = 0

    for r in rows:
        if is_row_anonymized(r):
            continue

        cur.execute(
            """
            UPDATE users
            SET name = ?,
                email = ?,
                personnummer = ?,
                address = ?,
                is_anonymized = 1,
                updated_at = ?
            WHERE id = ?
            """,
            (
                ANON_NAME,
                anonymize_email(r.email),
                anonymize_personnummer(r.personnummer),
                anonymize_address(r.address),
                now,
                r.id,
            ),
        )
        updated += 1

    conn.commit()
    return updated


def check_anonymization(conn: sqlite3.Connection) -> Tuple[int, int]:
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, name, email, personnummer, address, is_test_data, is_anonymized, created_at, updated_at
        FROM users
        WHERE is_test_data = 1
        """
    )
    rows = [UserRow(**dict(r)) for r in cur.fetchall()]
    total = len(rows)
    not_anon = sum(1 for r in rows if not is_row_anonymized(r))
    return total, not_anon


def anonymization_guard(conn: sqlite3.Connection) -> None:
   
    # self-startup kontrol
    _, not_anon = check_anonymization(conn)
    if not_anon > 0:
        fixed = anonymize_non_anonymized_test_rows(conn)
        print(f"[guard] fixed_startup={fixed}")

    # daglik kontrol
    today = dt.datetime.now().date().isoformat()
    last = meta_get(conn, "last_anonym_check_date")
    if last == today:
        return

    total, not_anon2 = check_anonymization(conn)
    if not_anon2 > 0:
        fixed2 = anonymize_non_anonymized_test_rows(conn)
        print(f"[guard] fixed_daily={fixed2}")

    print(f"[guard] daily_ok total_test_rows={total}")
    meta_set(conn, "last_anonym_check_date", today)



# -----------------------------
# Utility
# -----------------------------
def list_users(conn: sqlite3.Connection, limit: int = 50) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, name, email, personnummer, address, is_test_data, is_anonymized, created_at, updated_at
        FROM users
        ORDER BY id ASC
        LIMIT ?
        """,
        (limit,),
    )
    for r in cur.fetchall():
        print(dict(r))


def clear_test_data(conn: sqlite3.Connection) -> int:
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE is_test_data = 1")
    conn.commit()
    return cur.rowcount


# -----------------------------
# Tests
# -----------------------------
class AppTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.NamedTemporaryFile(delete=False)
        self.tmp.close()
        self.db_path = self.tmp.name
        self.conn = connect(self.db_path)
        init_db(self.conn)

    def tearDown(self) -> None:
        self.conn.close()
        try:
            os.unlink(self.db_path)
        except OSError:
            pass

    def test_seed_then_anonymize(self) -> None:
        inserted = seed_raw_test_data(self.conn, n=5)
        self.assertEqual(inserted, 5)

        total, not_anon = check_anonymization(self.conn)
        self.assertEqual(total, 5)
        self.assertEqual(not_anon, 5)

        fixed = anonymize_non_anonymized_test_rows(self.conn)
        self.assertEqual(fixed, 5)

        total2, not_anon2 = check_anonymization(self.conn)
        self.assertEqual(total2, 5)
        self.assertEqual(not_anon2, 0)

    def test_guard_enforces_only(self) -> None:
    # lägger in rå data
        seed_raw_test_data(self.conn, n=3)

    # guarden körs och fixar
        anonymization_guard(self.conn)

        total, not_anon = check_anonymization(self.conn)
        self.assertEqual(total, 3)
        self.assertEqual(not_anon, 0)


'''Funktionen build_parser() definierar programmets kommandoradsgränssnitt och 
specificerar vilka kommandon och argument applikationen accepterar. Gör koden mer
läsbar och underlättar hanteringen av användarinmatning.'''

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="GDPR-friendly test person register (SQLite) with Faker.")
    p.add_argument("--db", default=DEFAULT_DB_PATH, help="Path to SQLite DB (default: env DATABASE_PATH or ./test_users.db)")
    p.add_argument("--test", action="store_true", help="Run unit tests and exit")

    sub = p.add_subparsers(dest="cmd", required=False)
    sub.add_parser("init", help="Initialize database schema")

    seed_p = sub.add_parser("seed", help="Seed raw (non-anonymized) test data")
    seed_p.add_argument("-n", type=int, default=10, help="Number of rows")

    sub.add_parser("anonymize", help="Anonymize all non-anonymized test rows")
    sub.add_parser("check", help="Check anonymization status (counts)")
    sub.add_parser("list", help="List users")
    sub.add_parser("clear", help="Delete all test data")

    return p


def main(argv: list[str]) -> int:
    args = build_parser().parse_args(argv)

    if args.test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(AppTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        return 0 if result.wasSuccessful() else 1

    with connect(args.db) as conn:
        init_db(conn)

        cmd = args.cmd or "list"

        # Anonymization guard för alla kommandon utom de som skapar eller hanterar rå data
        if cmd not in ("seed", "list", "check", "anonymize"):
            anonymization_guard(conn)

        if cmd == "init":
            print("DB initialized.")
            return 0
        if cmd == "seed":
            inserted = seed_raw_test_data(conn, n=args.n)
            print(f"Seeded raw rows: {inserted}")
            return 0
        if cmd == "anonymize":
            fixed = anonymize_non_anonymized_test_rows(conn)
            print(f"Anonymized rows: {fixed}")
            return 0
        if cmd == "check":
            total, not_anon = check_anonymization(conn)
            print(f"total_test_rows={total} non_anonymized={not_anon}")
            return 0
        if cmd == "list":
            list_users(conn)
            return 0
        if cmd == "clear":
            deleted = clear_test_data(conn)
            print(f"Deleted test rows: {deleted}")
            return 0

        print(f"Unknown command: {cmd}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
