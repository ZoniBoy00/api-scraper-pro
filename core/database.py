"""
Database Manager - SQLite Data Storage
======================================

Manages SQLite database for API data persistence.
"""

import aiosqlite
from typing import Dict, Any, List, Optional
from loguru import logger
from datetime import datetime
import json
import os
from pathlib import Path


class DatabaseManager:
    """Manages SQLite database for API data."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        db_path = config.get('path', 'data/scraper.db')
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self.connection: Optional[aiosqlite.Connection] = None
        
    async def initialize(self) -> None:
        """Initialize database and create tables."""
        logger.info(f"Initializing database: {self.db_path}")
        self.connection = await aiosqlite.connect(self.db_path)
        await self._create_tables()
        logger.success("Database initialized")
    
    async def _create_tables(self) -> None:
        """Create database tables."""
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS api_endpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                method TEXT NOT NULL,
                first_seen TIMESTAMP NOT NULL,
                last_seen TIMESTAMP NOT NULL,
                call_count INTEGER DEFAULT 1,
                avg_response_size INTEGER,
                schema_json TEXT
            )
        """)
        
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS api_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint_id INTEGER NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                status_code INTEGER NOT NULL,
                response_body TEXT,
                response_headers TEXT,
                request_headers TEXT,
                response_size INTEGER,
                FOREIGN KEY (endpoint_id) REFERENCES api_endpoints (id)
            )
        """)
        
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS crawl_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                base_url TEXT NOT NULL,
                pages_crawled INTEGER DEFAULT 0,
                apis_found INTEGER DEFAULT 0,
                status TEXT DEFAULT 'running'
            )
        """)
        
        # Create indexes
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_api_endpoints_url ON api_endpoints(url)")
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_api_calls_endpoint ON api_calls(endpoint_id)")
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_api_calls_timestamp ON api_calls(timestamp)")
        
        await self.connection.commit()
        logger.debug("Database tables created")
    
    async def save_api_call(self, api_data: Dict[str, Any]) -> int:
        """Save API call to database."""
        try:
            endpoint_id = await self._get_or_create_endpoint(api_data)
            
            cursor = await self.connection.execute("""
                INSERT INTO api_calls (
                    endpoint_id, timestamp, status_code, 
                    response_body, response_headers, request_headers, response_size
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                endpoint_id, api_data['timestamp'], api_data['status'],
                json.dumps(api_data['response_body']),
                json.dumps(api_data['headers']),
                json.dumps(api_data['request_headers']),
                api_data['response_size']
            ))
            
            call_id = cursor.lastrowid
            await self._update_endpoint_stats(endpoint_id, api_data)
            await self.connection.commit()
            
            logger.debug(f"API call saved (ID: {call_id})")
            return call_id
            
        except Exception as e:
            logger.error(f"Failed to save API call: {e}")
            await self.connection.rollback()
            raise
    
    async def _get_or_create_endpoint(self, api_data: Dict[str, Any]) -> int:
        """Get endpoint ID or create new."""
        url = api_data['url']
        method = api_data['method']
        
        cursor = await self.connection.execute(
            "SELECT id FROM api_endpoints WHERE url = ? AND method = ?",
            (url, method)
        )
        row = await cursor.fetchone()
        
        if row:
            return row[0]
        
        now = datetime.utcnow().isoformat()
        schema_json = json.dumps(api_data.get('schema', {}))
        
        cursor = await self.connection.execute("""
            INSERT INTO api_endpoints (url, method, first_seen, last_seen, schema_json)
            VALUES (?, ?, ?, ?, ?)
        """, (url, method, now, now, schema_json))
        
        return cursor.lastrowid
    
    async def _update_endpoint_stats(self, endpoint_id: int, api_data: Dict[str, Any]) -> None:
        """Update endpoint statistics."""
        now = datetime.utcnow().isoformat()
        response_size = api_data['response_size']
        
        await self.connection.execute("""
            UPDATE api_endpoints 
            SET 
                last_seen = ?,
                call_count = call_count + 1,
                avg_response_size = (COALESCE(avg_response_size, 0) * (call_count - 1) + ?) / call_count
            WHERE id = ?
        """, (now, response_size, endpoint_id))
    
    async def get_all_endpoints(self) -> List[Dict[str, Any]]:
        """Get all API endpoints."""
        cursor = await self.connection.execute("""
            SELECT id, url, method, first_seen, last_seen, call_count, avg_response_size, schema_json
            FROM api_endpoints
            ORDER BY call_count DESC
        """)
        rows = await cursor.fetchall()
        
        return [
            {
                'id': row[0], 'url': row[1], 'method': row[2],
                'first_seen': row[3], 'last_seen': row[4],
                'call_count': row[5], 'avg_response_size': row[6],
                'schema': json.loads(row[7]) if row[7] else {}
            }
            for row in rows
        ]
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        cursor = await self.connection.execute("SELECT COUNT(*) FROM api_endpoints")
        total_endpoints = (await cursor.fetchone())[0]
        
        cursor = await self.connection.execute("SELECT COUNT(*) FROM api_calls")
        total_calls = (await cursor.fetchone())[0]
        
        db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
        
        cursor = await self.connection.execute("SELECT method, COUNT(*) FROM api_endpoints GROUP BY method")
        methods = dict(await cursor.fetchall())
        
        return {
            'total_endpoints': total_endpoints,
            'total_calls': total_calls,
            'database_size': db_size,
            'database_size_mb': round(db_size / 1024 / 1024, 2),
            'methods': methods
        }
    
    async def backup(self) -> str:
        """Create database backup."""
        if not self.config.get('auto_backup', True):
            return ""
        
        backup_dir = self.config.get('backup_dir', 'data/backups')
        Path(backup_dir).mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(backup_dir, f'scraper_backup_{timestamp}.db')
        
        async with aiosqlite.connect(backup_path) as backup_conn:
            await self.connection.backup(backup_conn)
        
        logger.info(f"Backup created: {backup_path}")
        await self._cleanup_old_backups(backup_dir)
        return backup_path
    
    async def _cleanup_old_backups(self, backup_dir: str) -> None:
        """Remove old backup files."""
        max_backups = self.config.get('max_backups', 5)
        backup_files = sorted(
            Path(backup_dir).glob('scraper_backup_*.db'),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        for old_backup in backup_files[max_backups:]:
            old_backup.unlink()
            logger.debug(f"Old backup removed: {old_backup}")
    
    async def clear_all_data(self) -> bool:
        """
        Clear all data from database (endpoints and API calls).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete all API calls first (foreign key constraint)
            await self.connection.execute("DELETE FROM api_calls")
            
            # Delete all endpoints
            await self.connection.execute("DELETE FROM api_endpoints")
            
            # Delete all sessions
            await self.connection.execute("DELETE FROM crawl_sessions")
            
            # Reset autoincrement
            await self.connection.execute("DELETE FROM sqlite_sequence WHERE name IN ('api_calls', 'api_endpoints', 'crawl_sessions')")
            
            await self.connection.commit()
            
            logger.info("All data cleared from database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear database: {e}")
            await self.connection.rollback()
            return False
    
    async def close(self) -> None:
        """Close database connection."""
        if self.connection:
            await self.connection.close()
            logger.debug("Database closed")
    
    async def __aenter__(self):
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
