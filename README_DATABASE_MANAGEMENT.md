# Database Management & Connection Pooling

This document describes the robust database management and connection pooling features implemented in the mcp-mem0 service.

## Overview

The database management system provides:
- **Connection Pooling**: Efficient database connection reuse
- **Health Monitoring**: Continuous database health checks
- **Retry Logic**: Automatic retry with exponential backoff
- **Connection Validation**: Pre-use connection testing
- **Monitoring Tools**: Real-time database status monitoring

## Features

### 1. Connection Pooling

The system uses PostgreSQL connection pooling with the following benefits:
- **Resource Efficiency**: Reuses connections instead of creating new ones
- **Performance**: Reduces connection overhead
- **Scalability**: Handles multiple concurrent requests efficiently
- **Resource Limits**: Prevents database overload

### 2. Health Monitoring

Continuous health monitoring includes:
- **Connection Testing**: Regular database connectivity tests
- **Response Time Tracking**: Monitors query performance
- **Pool Statistics**: Tracks connection pool utilization
- **Error Detection**: Identifies and reports connection issues

### 3. Retry Logic

Robust error handling with:
- **Exponential Backoff**: Increasing delays between retries
- **Configurable Attempts**: Customizable retry count
- **Error Classification**: Different handling for different error types
- **Graceful Degradation**: Service continues with reduced functionality

## Configuration

### Environment Variables

Add these settings to your `.env` file:

```bash
# Database Connection Management
DATABASE_POOL_SIZE=5                    # Minimum connections in pool
DATABASE_MAX_CONNECTIONS=20            # Maximum connections in pool
DATABASE_MAX_OVERFLOW=10               # Additional connections beyond max
DATABASE_POOL_TIMEOUT=30               # Connection timeout (seconds)
DATABASE_POOL_RECYCLE=3600             # Connection recycle time (seconds)
DATABASE_HEALTH_CHECK_INTERVAL=60      # Health check interval (seconds)
DATABASE_RETRY_ATTEMPTS=3              # Number of retry attempts
DATABASE_RETRY_DELAY=2.0               # Initial retry delay (seconds)
DATABASE_MAX_RETRY_DELAY=60.0          # Maximum retry delay (seconds)
```

### Recommended Settings

#### Development
```bash
DATABASE_POOL_SIZE=2
DATABASE_MAX_CONNECTIONS=5
DATABASE_HEALTH_CHECK_INTERVAL=120
```

#### Production
```bash
DATABASE_POOL_SIZE=10
DATABASE_MAX_CONNECTIONS=50
DATABASE_MAX_OVERFLOW=20
DATABASE_HEALTH_CHECK_INTERVAL=30
```

## Monitoring

### Health Check Endpoints

The service provides two health check tools:

#### 1. Basic Health Check
```bash
# Via MCP tool
health_check()
```
Returns basic service status for load balancers.

#### 2. Detailed Health Check
```bash
# Via MCP tool
detailed_health_check()
```
Returns comprehensive health information including:
- Service uptime and status
- Database connection health
- Connection pool statistics
- Memory usage
- Error details

### Database Monitoring Script

Use the provided monitoring script for real-time database status:

```bash
# Single health check
python monitor_database.py

# Continuous monitoring (30-second intervals)
python monitor_database.py --continuous

# Custom interval (10-second intervals)
python monitor_database.py --continuous --interval 10

# Export metrics to JSON
python monitor_database.py --export metrics.json

# JSON output
python monitor_database.py --json
```

### Monitoring Dashboard

The monitoring script provides a real-time dashboard showing:

```
============================================================
MCP-MEM0 DATABASE MONITORING DASHBOARD
============================================================
Timestamp: 2024-01-15 14:30:25

SERVICE STATUS:
  Status: HEALTHY
  Uptime: 2d 5h 30m 15s
  Memory: 45.2 MB
  Version: 1.0.0

DATABASE STATUS:
  Health: ✓ HEALTHY
  Last Check: 2024-01-15T14:30:25
  Response Time: 12.34 ms

CONNECTION POOL:
  Active: 3
  Available: 17
  Total: 20
  Utilization: 15.0%
  Min Pool: 5
  Max Pool: 20
============================================================
```

## Troubleshooting

### Common Issues

#### 1. Connection Pool Exhaustion
**Symptoms**: "Failed to get connection from pool" errors
**Solutions**:
- Increase `DATABASE_MAX_CONNECTIONS`
- Check for connection leaks
- Monitor pool utilization

#### 2. Database Timeouts
**Symptoms**: "Database operation timed out" errors
**Solutions**:
- Increase `DATABASE_POOL_TIMEOUT`
- Check database performance
- Optimize queries

#### 3. Health Check Failures
**Symptoms**: Database marked as unhealthy
**Solutions**:
- Check database server status
- Verify network connectivity
- Review database logs

### Debugging

Enable debug logging:
```bash
LOG_LEVEL=DEBUG
```

Check database manager status:
```python
from database_manager import get_database_manager
db_manager = get_database_manager()
print(db_manager.get_health_status())
print(db_manager.get_pool_stats())
```

## Performance Tuning

### Connection Pool Sizing

**Formula**: `Pool Size = (Peak Concurrent Requests × 2) + 5`

**Example**: If you have 20 peak concurrent requests:
- Pool Size: `(20 × 2) + 5 = 45`
- Max Connections: `45 + 10 = 55`

### Health Check Frequency

- **High Availability**: 30 seconds
- **Normal Operations**: 60 seconds
- **Development**: 120 seconds

### Retry Configuration

- **Network Issues**: 3-5 attempts, 2-5 second delays
- **Database Locks**: 2-3 attempts, 1-2 second delays
- **Resource Exhaustion**: 1-2 attempts, 5-10 second delays

## Integration

### With Load Balancers

Use the basic health check endpoint:
```bash
curl http://localhost:3003/health
```

### With Monitoring Systems

Use the detailed health check for comprehensive metrics:
```bash
curl http://localhost:3003/health/detailed
```

### With Alerting

Set up alerts based on:
- Service status != "healthy"
- Database response time > 1000ms
- Pool utilization > 80%
- Memory usage > 500MB

## Best Practices

1. **Monitor Pool Utilization**: Keep it below 80%
2. **Set Appropriate Timeouts**: Balance responsiveness and reliability
3. **Regular Health Checks**: Monitor database performance trends
4. **Connection Recycling**: Prevent stale connections
5. **Error Handling**: Implement proper retry logic
6. **Resource Monitoring**: Track memory and CPU usage
7. **Logging**: Enable structured logging for debugging

## Security Considerations

1. **Connection Encryption**: Use SSL/TLS for database connections
2. **Credential Management**: Store database credentials securely
3. **Access Control**: Limit database user permissions
4. **Audit Logging**: Log all database operations
5. **Network Security**: Use firewalls and VPNs

## Maintenance

### Regular Tasks

1. **Monitor Pool Statistics**: Check utilization patterns
2. **Review Health Logs**: Look for recurring issues
3. **Update Configuration**: Adjust settings based on usage
4. **Database Maintenance**: Regular VACUUM and ANALYZE
5. **Backup Verification**: Ensure backups are working

### Emergency Procedures

1. **Service Restart**: Restart the service if health checks fail
2. **Database Restart**: Restart database if connection issues persist
3. **Pool Reset**: Clear connection pool if corrupted
4. **Configuration Rollback**: Revert to known working settings
5. **Escalation**: Contact database administrator for persistent issues
