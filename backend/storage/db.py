# Nion Orchestration Engine - SQLite Storage
# Persistent storage layer for orchestration results

import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from config import config
from models.l1_models import L1TaskPlan
from models.l3_models import ActionItemsResult, RisksResult, DecisionsResult

logger = logging.getLogger(__name__)


class Storage:
    """
    SQLite storage layer for persisting orchestration results.
    
    Simple and MVP-friendly - no ORM, direct SQL.
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or config.storage.db_path
        self._ensure_schema()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _ensure_schema(self):
        """Create database schema if not exists"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Main orchestration maps table (original from design.md)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orchestration_maps (
                    id INTEGER PRIMARY KEY,
                    message_id TEXT,
                    map_text TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tasks table for L1 output
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    message_id TEXT,
                    task_id TEXT UNIQUE,
                    domain TEXT,
                    description TEXT,
                    priority TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Extractions table for L3 output
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS extractions (
                    id INTEGER PRIMARY KEY,
                    task_id TEXT REFERENCES tasks(task_id),
                    extraction_type TEXT,
                    data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Index for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tasks_message_id 
                ON tasks(message_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_extractions_task_id 
                ON extractions(task_id)
            """)
            
            logger.debug("Database schema initialized")
    
    def save_orchestration_map(
        self,
        message_id: str,
        map_text: str
    ) -> int:
        """Save an orchestration map and return its ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO orchestration_maps (message_id, map_text) VALUES (?, ?)",
                (message_id, map_text)
            )
            return cursor.lastrowid
    
    def save_task_plan(self, task_plan: L1TaskPlan) -> List[int]:
        """Save all tasks from a plan and return their IDs"""
        ids = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for task in task_plan.tasks:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO tasks 
                    (message_id, task_id, domain, description, priority)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        task_plan.source_message_id,
                        task.task_id,
                        task.domain,
                        task.description,
                        task.priority
                    )
                )
                ids.append(cursor.lastrowid)
        return ids
    
    def save_extraction(
        self,
        task_id: str,
        extraction_type: str,
        data: Dict[str, Any]
    ) -> int:
        """Save an extraction result"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO extractions (task_id, extraction_type, data)
                VALUES (?, ?, ?)
                """,
                (task_id, extraction_type, json.dumps(data))
            )
            return cursor.lastrowid
    
    def get_orchestration_map(self, message_id: str) -> Optional[Dict]:
        """Get the most recent orchestration map for a message"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM orchestration_maps 
                WHERE message_id = ? 
                ORDER BY created_at DESC 
                LIMIT 1
                """,
                (message_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_tasks_for_message(self, message_id: str) -> List[Dict]:
        """Get all tasks for a message"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM tasks WHERE message_id = ? ORDER BY task_id",
                (message_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def get_extractions_for_task(self, task_id: str) -> List[Dict]:
        """Get all extractions for a task"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM extractions WHERE task_id = ?",
                (task_id,)
            )
            rows = cursor.fetchall()
            result = []
            for row in rows:
                d = dict(row)
                d['data'] = json.loads(d['data'])
                result.append(d)
            return result


# Singleton instance
storage = Storage()
