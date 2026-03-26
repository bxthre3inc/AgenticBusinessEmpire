"""
schema.py — AgentOS Master Ledger DDL (V1.0-GENESIS)
Defines the absolute state architecture for Bxthre3 Inc.
"""

from __future__ import annotations
import logging
from typing import Any

logger = logging.getLogger("agentos.schema")

# ---------------------------------------------------------------------------
# CORE CONGLOMERATE DDL
# ---------------------------------------------------------------------------

CONGLOMERATE_DDL = """
-- WORKFORCE & GOVERNOR
CREATE TABLE IF NOT EXISTS workforce (
    employee_id     TEXT PRIMARY KEY,
    company_id      TEXT NOT NULL,
    department_id   TEXT NOT NULL,
    employee_type   TEXT NOT NULL, -- agentic | human | robotic
    role            TEXT NOT NULL,
    name            TEXT,
    status          TEXT DEFAULT 'active',
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS companies (
    company_id      TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    lifecycle_state TEXT DEFAULT 'IDEA', -- IDEA | VALIDATION | PROJECT | DIVISION | SUBSIDIARY | EXIT
    parent_id       TEXT DEFAULT 'bxthre3_inc',
    created_at      TEXT DEFAULT (datetime('now'))
);

-- NATIVE CAPABILITY SUITE (BOARDS & DOCS)
CREATE TABLE IF NOT EXISTS boards (
    board_id        TEXT PRIMARY KEY,
    company_id      TEXT NOT NULL,
    name            TEXT NOT NULL,
    config_json     TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS cells (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    board_id        TEXT NOT NULL,
    row_id          TEXT NOT NULL,
    col_name        TEXT NOT NULL,
    value           TEXT,
    last_updated    TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS docs (
    doc_id          TEXT PRIMARY KEY,
    company_id      TEXT NOT NULL,
    title           TEXT NOT NULL,
    owner_id        TEXT NOT NULL,
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS doc_blocks (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id          TEXT NOT NULL,
    block_type      TEXT NOT NULL,
    content         TEXT,
    position        INTEGER NOT NULL
);

-- FINANCIAL ORCHESTRATION LAYER
CREATE TABLE IF NOT EXISTS invoices (
    invoice_id      TEXT PRIMARY KEY,
    company_id      TEXT NOT NULL,
    entity_id       TEXT NOT NULL,
    amount          REAL NOT NULL,
    currency        TEXT DEFAULT 'USD',
    stripe_id       TEXT,
    status          TEXT DEFAULT 'unpaid',
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS payouts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id      TEXT NOT NULL,
    entity_id       TEXT NOT NULL,
    amount          REAL NOT NULL,
    stripe_tx_id    TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS budgets (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id      TEXT NOT NULL,
    dept_id         TEXT NOT NULL,
    amount          REAL NOT NULL,
    period          TEXT DEFAULT 'monthly',
    status          TEXT DEFAULT 'active',
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS tax_provisions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id      TEXT NOT NULL,
    amount          REAL NOT NULL,
    tax_type        TEXT DEFAULT 'income',
    due_date        TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS funding_rounds (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id      TEXT NOT NULL,
    amount          REAL NOT NULL,
    funding_type    TEXT NOT NULL, -- grant | equity | debt
    source          TEXT NOT NULL,
    terms_json      TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);

-- MESSENGER & COMMANDS
CREATE TABLE IF NOT EXISTS messages (
    message_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id      TEXT NOT NULL,
    sender_id       TEXT NOT NULL,
    receiver_id     TEXT NOT NULL,
    content         TEXT NOT NULL,
    status          TEXT DEFAULT 'sent',
    created_at      TEXT DEFAULT (datetime('now'))
);

-- ENTITIES & STRATEGY
CREATE TABLE IF NOT EXISTS entities (
    entity_id       TEXT PRIMARY KEY,
    company_id      TEXT NOT NULL,
    type            TEXT NOT NULL, -- client | partner | funder
    name            TEXT NOT NULL,
    metadata_json   TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS milestones (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id      TEXT NOT NULL,
    dept_id         TEXT NOT NULL,
    title           TEXT NOT NULL,
    status          TEXT DEFAULT 'planned',
    deadline        TEXT
);
"""

LEGACY_DDL = """
CREATE TABLE IF NOT EXISTS recursive_logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    patch_id        TEXT NOT NULL UNIQUE,
    applied_at      TEXT DEFAULT (datetime('now')),
    target_file     TEXT NOT NULL,
    outcome         TEXT DEFAULT 'success'
);
"""

ALL_DDL = [CONGLOMERATE_DDL, LEGACY_DDL]

async def apply() -> None:
    import aiosqlite
    import os
    _DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "runtime", "agentos.db")
    
    async with aiosqlite.connect(_DB_PATH) as db:
        for ddl in ALL_DDL:
            await db.executescript(ddl)
        await db.commit()
    logger.info("[schema] v1.0-GENESIS Master Ledger applied.")
