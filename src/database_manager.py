"""
Database Connection Manager for mcp-mem0 server.
Provides robust database connection management with pooling, health checks, and retry logic.
"""

import os
import time
import asyncio
import logging
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
from dataclasses import dataclass
from urllib.parse import urlparse
import psycopg2
from psycopg2 import pool
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import threading
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database configuration parameters."""
    connection_string: str
    min_connections: int = 5
    max_connections: int = 20
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600  # 1 hour
    health_check_interval: int = 60  # 1 minute
    retry_attempts: int = 3
    retry_delay: float = 2.0
    max_retry_delay: float = 60.0

@dataclass
class ConnectionHealth:
    """Database connection health status."""
    is_healthy: bool
    last_check: datetime
    response_time_ms: float
    active_connections: int
    total_connections: int
    error_message: Optional[str] = None

class DatabaseManager:
    """
    Robust database connection manager with pooling, health monitoring, and retry logic.
    """
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.connection_pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None
        self.health_status = ConnectionHealth(
            is_healthy=False,
            last_check=datetime.min,
            response_time_ms=0.0,
            active_connections=0,
            total_connections=0
        )
        self._lock = threading.Lock()
        self._health_check_task: Optional[asyncio.Task] = None
        self._shutdown_event = threading.Event()
        
    def initialize(self) -> bool:
        """
        Initialize the database connection pool.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing database connection pool...")
            
            # Parse connection string to extract components
            parsed_url = urlparse(self.config.connection_string)
            
            # Create connection pool
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=self.config.min_connections,
                maxconn=self.config.max_connections,
                dsn=self.config.connection_string,
                options=f"-c statement_timeout={self.config.pool_timeout * 1000}"
            )
            
            # Test initial connection
            if self._test_connection():
                logger.info(f"Database connection pool initialized successfully with {self.config.min_connections}-{self.config.max_connections} connections")
                self._start_health_monitoring()
                return True
            else:
                logger.error("Failed to establish initial database connection")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            return False
    
    def _test_connection(self) -> bool:
        """
        Test database connection and update health status.
        
        Returns:
            bool: True if connection is healthy, False otherwise
        """
        start_time = time.time()
        
        try:
            if not self.connection_pool:
                return False
                
            # Get a connection from the pool
            conn = self.connection_pool.getconn()
            if not conn:
                return False
                
            try:
                # Test the connection with a simple query
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    
                # Update health status
                response_time = (time.time() - start_time) * 1000
                
                with self._lock:
                    self.health_status = ConnectionHealth(
                        is_healthy=True,
                        last_check=datetime.now(),
                        response_time_ms=response_time,
                        active_connections=self.connection_pool.closed,
                        total_connections=self.connection_pool.maxconn,
                        error_message=None
                    )
                
                logger.debug(f"Database health check passed - response time: {response_time:.2f}ms")
                return True
                
            finally:
                # Return connection to pool
                self.connection_pool.putconn(conn)
                
        except Exception as e:
            error_msg = f"Database health check failed: {e}"
            logger.warning(error_msg)
            
            with self._lock:
                self.health_status = ConnectionHealth(
                    is_healthy=False,
                    last_check=datetime.now(),
                    response_time_ms=(time.time() - start_time) * 1000,
                    active_connections=self.connection_pool.closed if self.connection_pool else 0,
                    total_connections=self.connection_pool.maxconn if self.connection_pool else 0,
                    error_message=error_msg
                )
            
            return False
    
    def _start_health_monitoring(self):
        """Start background health monitoring task."""
        def health_monitor():
            while not self._shutdown_event.is_set():
                try:
                    self._test_connection()
                    time.sleep(self.config.health_check_interval)
                except Exception as e:
                    logger.error(f"Health monitoring error: {e}")
                    time.sleep(5)  # Short delay before retrying
        
        health_thread = threading.Thread(target=health_monitor, daemon=True)
        health_thread.start()
        logger.info("Database health monitoring started")
    
    @asynccontextmanager
    async def get_connection(self):
        """
        Get a database connection from the pool with retry logic.
        
        Yields:
            psycopg2.connection: Database connection
        """
        connection = None
        last_exception = None
        
        for attempt in range(self.config.retry_attempts):
            try:
                if not self.connection_pool:
                    raise RuntimeError("Database connection pool not initialized")
                
                # Get connection from pool
                connection = self.connection_pool.getconn()
                if not connection:
                    raise RuntimeError("Failed to get connection from pool")
                
                # Test connection before yielding
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                
                logger.debug("Database connection acquired successfully")
                yield connection
                return
                
            except Exception as e:
                last_exception = e
                logger.warning(f"Database connection attempt {attempt + 1} failed: {e}")
                
                # Clean up failed connection
                if connection:
                    try:
                        self.connection_pool.putconn(connection, close=True)
                    except:
                        pass
                    connection = None
                
                # Calculate retry delay with exponential backoff
                if attempt < self.config.retry_attempts - 1:
                    delay = min(
                        self.config.retry_delay * (2 ** attempt),
                        self.config.max_retry_delay
                    )
                    logger.info(f"Retrying database connection in {delay:.1f} seconds...")
                    await asyncio.sleep(delay)
        
        # All retry attempts failed
        error_msg = f"Failed to get database connection after {self.config.retry_attempts} attempts: {last_exception}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    
    def get_health_status(self) -> ConnectionHealth:
        """
        Get current database health status.
        
        Returns:
            ConnectionHealth: Current health status
        """
        with self._lock:
            return self.health_status
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """
        Get connection pool statistics.
        
        Returns:
            Dict[str, Any]: Pool statistics
        """
        if not self.connection_pool:
            return {"error": "Connection pool not initialized"}
        
        return {
            "min_connections": self.connection_pool.minconn,
            "max_connections": self.connection_pool.maxconn,
            "active_connections": self.connection_pool.closed,
            "available_connections": self.connection_pool.maxconn - self.connection_pool.closed,
            "pool_utilization": f"{(self.connection_pool.closed / self.connection_pool.maxconn) * 100:.1f}%"
        }
    
    def close(self):
        """Close the database connection pool and cleanup resources."""
        logger.info("Closing database connection pool...")
        
        # Signal health monitoring to stop
        self._shutdown_event.set()
        
        # Close connection pool
        if self.connection_pool:
            try:
                self.connection_pool.closeall()
                logger.info("Database connection pool closed successfully")
            except Exception as e:
                logger.error(f"Error closing database connection pool: {e}")
            finally:
                self.connection_pool = None

def create_database_config() -> DatabaseConfig:
    """
    Create database configuration from environment variables.
    
    Returns:
        DatabaseConfig: Configured database settings
    """
    connection_string = os.getenv('DATABASE_URL')
    if not connection_string:
        raise ValueError("DATABASE_URL environment variable is required")
    
    return DatabaseConfig(
        connection_string=connection_string,
        min_connections=int(os.getenv('DATABASE_POOL_SIZE', '5')),
        max_connections=int(os.getenv('DATABASE_MAX_CONNECTIONS', '20')),
        max_overflow=int(os.getenv('DATABASE_MAX_OVERFLOW', '10')),
        pool_timeout=int(os.getenv('DATABASE_POOL_TIMEOUT', '30')),
        pool_recycle=int(os.getenv('DATABASE_POOL_RECYCLE', '3600')),
        health_check_interval=int(os.getenv('DATABASE_HEALTH_CHECK_INTERVAL', '60')),
        retry_attempts=int(os.getenv('DATABASE_RETRY_ATTEMPTS', '3')),
        retry_delay=float(os.getenv('DATABASE_RETRY_DELAY', '2.0')),
        max_retry_delay=float(os.getenv('DATABASE_MAX_RETRY_DELAY', '60.0'))
    )

# Global database manager instance
_db_manager: Optional[DatabaseManager] = None

def get_database_manager() -> DatabaseManager:
    """
    Get the global database manager instance.
    
    Returns:
        DatabaseManager: The database manager instance
    """
    global _db_manager
    
    if _db_manager is None:
        config = create_database_config()
        _db_manager = DatabaseManager(config)
        
        if not _db_manager.initialize():
            raise RuntimeError("Failed to initialize database manager")
    
    return _db_manager

def close_database_manager():
    """Close the global database manager."""
    global _db_manager
    
    if _db_manager:
        _db_manager.close()
        _db_manager = None
