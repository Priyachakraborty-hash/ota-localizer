import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
DB_PATH = "ota_localizer.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS releases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo TEXT NOT NULL,
            version TEXT NOT NULL,
            name TEXT,
            content TEXT,
            url TEXT,
            published_at TEXT,
            language TEXT DEFAULT 'en',
            translated_name TEXT,
            translated_content TEXT,
            fetched_at TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS health_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT,
            status TEXT,
            details TEXT,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()
    logger.info("Database initialized.")


def save_release(release, language="en"):
    """Save a single release, skipping duplicates."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT id FROM releases WHERE repo=? AND version=? AND language=?",
        (release["repo"], release["version"], language)
    )
    if c.fetchone():
        conn.close()
        return False  # Already exists

    c.execute("""
        INSERT INTO releases
        (repo, version, name, content, url, published_at, language,
         translated_name, translated_content, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        release["repo"],
        release["version"],
        release.get("name", ""),
        release.get("content", ""),
        release.get("url", ""),
        release.get("published_at", ""),
        language,
        release.get("translated_name", ""),
        release.get("translated_content", ""),
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()
    return True


def save_releases(releases, language="en"):
    """Save a list of releases, return count of new ones saved."""
    count = sum(1 for r in releases if save_release(r, language))
    logger.info(f"Saved {count} new releases to DB (lang={language}).")
    return count


def get_releases(language="en", repo=None):
    """Get releases filtered by language and optionally by repo."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if repo:
        c.execute(
            "SELECT * FROM releases WHERE language=? AND repo=? ORDER BY fetched_at DESC",
            (language, repo)
        )
    else:
        c.execute(
            "SELECT * FROM releases WHERE language=? ORDER BY fetched_at DESC",
            (language,)
        )
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def log_health(event, status, details=""):
    """Log automation health events for monitoring."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO health_log (event, status, details, timestamp) VALUES (?, ?, ?, ?)",
        (event, status, details, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


def get_health_log(limit=20):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM health_log ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_stats():
    """Return summary stats for the monitoring dashboard."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM releases")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(DISTINCT repo) FROM releases")
    repos = c.fetchone()[0]
    c.execute("SELECT COUNT(DISTINCT language) FROM releases")
    langs = c.fetchone()[0]
    conn.close()
    return {"total_releases": total, "repos_tracked": repos, "languages": langs}
