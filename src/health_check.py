"""
Health check endpoints and monitoring for mcp-mem0 server.
"""

import asyncio
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json

from database_manager import get_database_manager, ConnectionHealth

@dataclass
class ServiceHealth:
    """Overall service health status."""
    status: str  # "healthy", "degraded", "unhealthy"
    timestamp: datetime
    uptime_seconds: float
    database: ConnectionHealth
    memory_usage_mb: float
    version: str = "1.0.0"

class HealthChecker:
    """Service health monitoring and reporting."""
    
    def __init__(self):
        self.start_time = time.time()
        self._last_health_check = None
        self._health_cache_duration = 30  # Cache health status for 30 seconds
    
    def get_uptime(self) -> float:
        """Get service uptime in seconds."""
        return time.time() - self.start_time
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            # Fallback if psutil is not available
            return 0.0
    
    async def get_health_status(self, force_refresh: bool = False) -> ServiceHealth:
        """
        Get comprehensive service health status.
        
        Args:
            force_refresh: Force refresh of cached health data
            
        Returns:
            ServiceHealth: Current service health status
        """
        # Use cached data if available and not forcing refresh
        if (not force_refresh and 
            self._last_health_check and 
            (datetime.now() - self._last_health_check).seconds < self._health_cache_duration):
            return self._last_health_check
        
        try:
            # Get database health
            db_manager = get_database_manager()
            db_health = db_manager.get_health_status()
            
            # Determine overall status
            if db_health.is_healthy:
                status = "healthy"
            elif db_health.last_check > datetime.now() - timedelta(minutes=5):
                status = "degraded"  # Recent check but unhealthy
            else:
                status = "unhealthy"  # No recent successful check
            
            health = ServiceHealth(
                status=status,
                timestamp=datetime.now(),
                uptime_seconds=self.get_uptime(),
                database=db_health,
                memory_usage_mb=self.get_memory_usage()
            )
            
            self._last_health_check = health
            return health
            
        except Exception as e:
            # If we can't get health status, return unhealthy
            return ServiceHealth(
                status="unhealthy",
                timestamp=datetime.now(),
                uptime_seconds=self.get_uptime(),
                database=ConnectionHealth(
                    is_healthy=False,
                    last_check=datetime.now(),
                    response_time_ms=0.0,
                    active_connections=0,
                    total_connections=0,
                    error_message=f"Health check failed: {str(e)}"
                ),
                memory_usage_mb=self.get_memory_usage()
            )
    
    def get_detailed_status(self) -> Dict[str, Any]:
        """
        Get detailed service status including database pool statistics.
        
        Returns:
            Dict[str, Any]: Detailed service status
        """
        try:
            db_manager = get_database_manager()
            health = asyncio.run(self.get_health_status(force_refresh=True))
            pool_stats = db_manager.get_pool_stats()
            
            return {
                "service": {
                    "status": health.status,
                    "uptime_seconds": health.uptime_seconds,
                    "uptime_human": str(timedelta(seconds=int(health.uptime_seconds))),
                    "memory_usage_mb": health.memory_usage_mb,
                    "version": health.version,
                    "timestamp": health.timestamp.isoformat()
                },
                "database": {
                    "is_healthy": health.database.is_healthy,
                    "last_check": health.database.last_check.isoformat(),
                    "response_time_ms": health.database.response_time_ms,
                    "active_connections": health.database.active_connections,
                    "total_connections": health.database.total_connections,
                    "error_message": health.database.error_message,
                    "pool_stats": pool_stats
                }
            }
        except Exception as e:
            return {
                "service": {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                },
                "database": {
                    "is_healthy": False,
                    "error": str(e)
                }
            }

# Global health checker instance
_health_checker: Optional[HealthChecker] = None

def get_health_checker() -> HealthChecker:
    """Get the global health checker instance."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker

async def health_check_endpoint() -> str:
    """
    Health check endpoint for load balancers and monitoring.
    
    Returns:
        str: JSON response with health status
    """
    health_checker = get_health_checker()
    health = await health_checker.get_health_status()
    
    # Return simple status for load balancers
    return json.dumps({
        "status": health.status,
        "timestamp": health.timestamp.isoformat(),
        "uptime_seconds": health.uptime_seconds
    }, indent=2)

async def detailed_health_endpoint() -> str:
    """
    Detailed health check endpoint for monitoring and debugging.
    
    Returns:
        str: JSON response with detailed health information
    """
    health_checker = get_health_checker()
    detailed_status = health_checker.get_detailed_status()
    
    return json.dumps(detailed_status, indent=2, default=str)
