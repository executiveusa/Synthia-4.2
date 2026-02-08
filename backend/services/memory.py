"""
Synthia 4.2 - Persistent Memory System

SQLite-backed memory that persists across sessions.
Each client gets their own memory space. Synthia never forgets.

Memory types:
- conversation: Full chat history per client
- facts: Extracted facts about clients (business, preferences, etc.)
- knowledge: Loaded from PDFs and training data (shared across all clients)
- context: Short-term working memory for current session
"""

import os
import json
import sqlite3
import logging
import hashlib
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

# DB lives alongside the backend code
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "synthia_memory.db")


def _ensure_db_dir():
    Path(os.path.dirname(DB_PATH)).mkdir(parents=True, exist_ok=True)


def _get_conn() -> sqlite3.Connection:
    _ensure_db_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create all tables if they don't exist."""
    conn = _get_conn()
    conn.executescript("""
        -- Clients table
        CREATE TABLE IF NOT EXISTS clients (
            client_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            language TEXT DEFAULT 'en',
            niche TEXT DEFAULT '',
            company TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );

        -- Conversation history (per client)
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id TEXT NOT NULL,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
            content TEXT NOT NULL,
            language TEXT DEFAULT 'en',
            timestamp TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (client_id) REFERENCES clients(client_id)
        );

        -- Extracted facts about clients
        CREATE TABLE IF NOT EXISTS client_facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id TEXT NOT NULL,
            category TEXT NOT NULL,
            fact TEXT NOT NULL,
            confidence REAL DEFAULT 1.0,
            source TEXT DEFAULT 'conversation',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (client_id) REFERENCES clients(client_id)
        );

        -- Knowledge base (from PDFs, training data - shared)
        CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            chunk_index INTEGER DEFAULT 0,
            content TEXT NOT NULL,
            content_hash TEXT UNIQUE,
            category TEXT DEFAULT 'general',
            created_at TEXT DEFAULT (datetime('now'))
        );

        -- Client-agent assignments
        CREATE TABLE IF NOT EXISTS agent_assignments (
            client_id TEXT PRIMARY KEY,
            agent_name TEXT NOT NULL DEFAULT 'Synthia',
            personality_notes TEXT DEFAULT '',
            priority TEXT DEFAULT 'normal',
            assigned_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (client_id) REFERENCES clients(client_id)
        );

        -- Indexes for fast lookups
        CREATE INDEX IF NOT EXISTS idx_conv_client ON conversations(client_id, timestamp);
        CREATE INDEX IF NOT EXISTS idx_facts_client ON client_facts(client_id, category);
        CREATE INDEX IF NOT EXISTS idx_knowledge_cat ON knowledge(category);
    """)
    conn.commit()
    conn.close()
    logger.info("Memory database initialized at %s", DB_PATH)


class MemoryStore:
    """
    Persistent memory for Synthia. Never forgets a client.
    
    Usage:
        mem = MemoryStore()
        mem.remember_client("phone:+13234842914", "Dennis", phone="+13234842914")
        mem.add_message("phone:+13234842914", "session1", "user", "I need a landing page")
        context = mem.get_client_context("phone:+13234842914")
    """

    def __init__(self):
        init_db()

    # ─── Client Management ──────────────────────────────────

    def remember_client(
        self,
        client_id: str,
        name: str,
        phone: str = "",
        email: str = "",
        language: str = "en",
        niche: str = "",
        company: str = "",
    ) -> None:
        """Create or update a client record."""
        conn = _get_conn()
        conn.execute("""
            INSERT INTO clients (client_id, name, phone, email, language, niche, company, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(client_id) DO UPDATE SET
                name = COALESCE(NULLIF(excluded.name, ''), clients.name),
                phone = COALESCE(NULLIF(excluded.phone, ''), clients.phone),
                email = COALESCE(NULLIF(excluded.email, ''), clients.email),
                language = COALESCE(NULLIF(excluded.language, ''), clients.language),
                niche = COALESCE(NULLIF(excluded.niche, ''), clients.niche),
                company = COALESCE(NULLIF(excluded.company, ''), clients.company),
                updated_at = datetime('now')
        """, (client_id, name, phone, email, language, niche, company))
        conn.commit()
        conn.close()

    def get_client(self, client_id: str) -> Optional[dict]:
        """Get client info by ID."""
        conn = _get_conn()
        row = conn.execute("SELECT * FROM clients WHERE client_id = ?", (client_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    def find_client_by_phone(self, phone: str) -> Optional[dict]:
        """Find client by phone number."""
        # Normalize phone
        phone_clean = phone.replace(" ", "").replace("-", "")
        if not phone_clean.startswith("+"):
            phone_clean = f"+{phone_clean}"
        
        conn = _get_conn()
        row = conn.execute(
            "SELECT * FROM clients WHERE phone = ? OR client_id = ?",
            (phone_clean, f"phone:{phone_clean}")
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    def list_clients(self) -> list[dict]:
        """List all clients."""
        conn = _get_conn()
        rows = conn.execute("SELECT * FROM clients ORDER BY updated_at DESC").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # ─── Conversation History ───────────────────────────────

    def add_message(
        self,
        client_id: str,
        session_id: str,
        role: str,
        content: str,
        language: str = "en",
    ) -> None:
        """Store a conversation message."""
        conn = _get_conn()
        conn.execute(
            "INSERT INTO conversations (client_id, session_id, role, content, language) VALUES (?, ?, ?, ?, ?)",
            (client_id, session_id, role, content, language)
        )
        conn.commit()
        conn.close()

    def get_recent_messages(
        self,
        client_id: str,
        limit: int = 20,
        session_id: Optional[str] = None,
    ) -> list[dict]:
        """Get recent conversation messages for a client."""
        conn = _get_conn()
        if session_id:
            rows = conn.execute(
                "SELECT role, content, language, timestamp FROM conversations "
                "WHERE client_id = ? AND session_id = ? ORDER BY timestamp DESC LIMIT ?",
                (client_id, session_id, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT role, content, language, timestamp FROM conversations "
                "WHERE client_id = ? ORDER BY timestamp DESC LIMIT ?",
                (client_id, limit)
            ).fetchall()
        conn.close()
        # Return in chronological order
        return [dict(r) for r in reversed(rows)]

    def get_all_history(self, client_id: str) -> list[dict]:
        """Get full conversation history for a client."""
        conn = _get_conn()
        rows = conn.execute(
            "SELECT role, content, language, session_id, timestamp FROM conversations "
            "WHERE client_id = ? ORDER BY timestamp ASC",
            (client_id,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # ─── Client Facts ───────────────────────────────────────

    def add_fact(
        self,
        client_id: str,
        category: str,
        fact: str,
        confidence: float = 1.0,
        source: str = "conversation",
    ) -> None:
        """Store an extracted fact about a client."""
        conn = _get_conn()
        # Avoid duplicates
        existing = conn.execute(
            "SELECT id FROM client_facts WHERE client_id = ? AND fact = ?",
            (client_id, fact)
        ).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO client_facts (client_id, category, fact, confidence, source) VALUES (?, ?, ?, ?, ?)",
                (client_id, category, fact, confidence, source)
            )
            conn.commit()
        conn.close()

    def get_facts(self, client_id: str, category: Optional[str] = None) -> list[dict]:
        """Get facts about a client, optionally filtered by category."""
        conn = _get_conn()
        if category:
            rows = conn.execute(
                "SELECT category, fact, confidence, source FROM client_facts "
                "WHERE client_id = ? AND category = ? ORDER BY confidence DESC",
                (client_id, category)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT category, fact, confidence, source FROM client_facts "
                "WHERE client_id = ? ORDER BY category, confidence DESC",
                (client_id,)
            ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # ─── Knowledge Base ─────────────────────────────────────

    def add_knowledge(
        self,
        source: str,
        content: str,
        category: str = "general",
        chunk_index: int = 0,
    ) -> bool:
        """
        Add knowledge to the shared knowledge base.
        Returns True if new, False if duplicate.
        """
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        conn = _get_conn()
        try:
            conn.execute(
                "INSERT INTO knowledge (source, chunk_index, content, content_hash, category) VALUES (?, ?, ?, ?, ?)",
                (source, chunk_index, content, content_hash, category)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False

    def search_knowledge(self, query: str, category: Optional[str] = None, limit: int = 5) -> list[dict]:
        """
        Simple keyword search across knowledge base.
        For production, use vector embeddings (e.g., sentence-transformers).
        """
        conn = _get_conn()
        # SQLite FTS-like search using LIKE
        query_terms = query.lower().split()
        conditions = " AND ".join(["LOWER(content) LIKE ?"] * len(query_terms))
        params = [f"%{term}%" for term in query_terms]

        if category:
            conditions += " AND category = ?"
            params.append(category)

        rows = conn.execute(
            f"SELECT source, content, category, chunk_index FROM knowledge "
            f"WHERE {conditions} ORDER BY id DESC LIMIT ?",
            params + [limit]
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_all_knowledge(self, category: Optional[str] = None) -> list[dict]:
        """Get all knowledge, optionally filtered by category."""
        conn = _get_conn()
        if category:
            rows = conn.execute(
                "SELECT source, content, category FROM knowledge WHERE category = ? ORDER BY source, chunk_index",
                (category,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT source, content, category FROM knowledge ORDER BY source, chunk_index"
            ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # ─── Agent Assignments ──────────────────────────────────

    def assign_agent(
        self,
        client_id: str,
        agent_name: str = "Synthia",
        personality_notes: str = "",
        priority: str = "normal",
    ) -> None:
        """Assign a specific agent persona to a client."""
        conn = _get_conn()
        conn.execute("""
            INSERT INTO agent_assignments (client_id, agent_name, personality_notes, priority)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(client_id) DO UPDATE SET
                agent_name = excluded.agent_name,
                personality_notes = excluded.personality_notes,
                priority = excluded.priority
        """, (client_id, agent_name, personality_notes, priority))
        conn.commit()
        conn.close()

    def get_agent_assignment(self, client_id: str) -> Optional[dict]:
        """Get agent assignment for a client."""
        conn = _get_conn()
        row = conn.execute(
            "SELECT * FROM agent_assignments WHERE client_id = ?", (client_id,)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    # ─── Context Builder ────────────────────────────────────

    def get_client_context(self, client_id: str, max_history: int = 10) -> str:
        """
        Build a complete context string for the LLM about this client.
        Includes: client info, facts, recent history, relevant knowledge.
        """
        parts = []

        # Client info
        client = self.get_client(client_id)
        if client:
            parts.append(f"CLIENT: {client['name']}")
            if client.get('company'):
                parts.append(f"  Company: {client['company']}")
            if client.get('niche'):
                parts.append(f"  Niche: {client['niche']}")
            if client.get('language'):
                parts.append(f"  Preferred language: {client['language']}")
            if client.get('notes'):
                parts.append(f"  Notes: {client['notes']}")

        # Facts
        facts = self.get_facts(client_id)
        if facts:
            parts.append("\nKNOWN FACTS ABOUT THIS CLIENT:")
            for f in facts[:15]:
                parts.append(f"  [{f['category']}] {f['fact']}")

        # Agent assignment
        assignment = self.get_agent_assignment(client_id)
        if assignment and assignment.get("personality_notes"):
            parts.append(f"\nAGENT NOTES: {assignment['personality_notes']}")

        # Recent conversation
        history = self.get_recent_messages(client_id, limit=max_history)
        if history:
            parts.append("\nRECENT CONVERSATION HISTORY:")
            for msg in history:
                parts.append(f"  {msg['role']}: {msg['content'][:300]}")

        return "\n".join(parts) if parts else ""

    # ─── Stats ──────────────────────────────────────────────

    def stats(self) -> dict:
        """Get memory stats."""
        conn = _get_conn()
        clients = conn.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
        messages = conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
        facts = conn.execute("SELECT COUNT(*) FROM client_facts").fetchone()[0]
        knowledge = conn.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0]
        conn.close()
        return {
            "clients": clients,
            "messages": messages,
            "facts": facts,
            "knowledge_chunks": knowledge,
            "db_path": DB_PATH,
        }


# Singleton
_memory: Optional[MemoryStore] = None


def get_memory_store() -> MemoryStore:
    global _memory
    if _memory is None:
        _memory = MemoryStore()
    return _memory


__all__ = ["MemoryStore", "get_memory_store"]
