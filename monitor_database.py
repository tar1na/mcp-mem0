#!/usr/bin/env python3
"""
Database monitoring script for mcp-mem0 service.
Provides real-time monitoring of database connections and health.
"""

import os
import sys
import time
import json
import argparse
from datetime import datetime
from typing import Dict, Any

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database_manager import get_database_manager, close_database_manager
from health_check import get_health_checker

def format_uptime(seconds: float) -> str:
    """Format uptime in human-readable format."""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m {seconds}s"
    elif hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def print_status_table(health_data: Dict[str, Any]):
    """Print a formatted status table."""
    print("\n" + "="*60)
    print("MCP-MEM0 DATABASE MONITORING DASHBOARD")
    print("="*60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Service Status
    service = health_data.get('service', {})
    print("SERVICE STATUS:")
    print(f"  Status: {service.get('status', 'unknown').upper()}")
    print(f"  Uptime: {service.get('uptime_human', 'unknown')}")
    print(f"  Memory: {service.get('memory_usage_mb', 0):.1f} MB")
    print(f"  Version: {service.get('version', 'unknown')}")
    print()
    
    # Database Status
    database = health_data.get('database', {})
    print("DATABASE STATUS:")
    print(f"  Health: {'✓ HEALTHY' if database.get('is_healthy') else '✗ UNHEALTHY'}")
    print(f"  Last Check: {database.get('last_check', 'never')}")
    print(f"  Response Time: {database.get('response_time_ms', 0):.2f} ms")
    print()
    
    # Connection Pool Stats
    pool_stats = database.get('pool_stats', {})
    if 'error' not in pool_stats:
        print("CONNECTION POOL:")
        print(f"  Active: {pool_stats.get('active_connections', 0)}")
        print(f"  Available: {pool_stats.get('available_connections', 0)}")
        print(f"  Total: {pool_stats.get('total_connections', 0)}")
        print(f"  Utilization: {pool_stats.get('pool_utilization', '0%')}")
        print(f"  Min Pool: {pool_stats.get('min_connections', 0)}")
        print(f"  Max Pool: {pool_stats.get('max_connections', 0)}")
    else:
        print(f"  Pool Error: {pool_stats.get('error')}")
    
    # Error Information
    if database.get('error_message'):
        print()
        print("ERRORS:")
        print(f"  {database.get('error_message')}")
    
    print("="*60)

def monitor_continuous(interval: int = 30):
    """Continuously monitor database status."""
    print("Starting continuous database monitoring...")
    print(f"Refresh interval: {interval} seconds")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            try:
                health_checker = get_health_checker()
                health_data = health_checker.get_detailed_status()
                print_status_table(health_data)
                
                # Clear screen for next update (optional)
                if os.name == 'nt':  # Windows
                    os.system('cls')
                else:  # Unix/Linux/Mac
                    os.system('clear')
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print("\nMonitoring stopped by user")
                break
            except Exception as e:
                print(f"\nError during monitoring: {e}")
                time.sleep(5)  # Wait before retrying
                
    finally:
        close_database_manager()

def monitor_single():
    """Run a single health check."""
    try:
        health_checker = get_health_checker()
        health_data = health_checker.get_detailed_status()
        print_status_table(health_data)
        
        # Exit with appropriate code
        service_status = health_data.get('service', {}).get('status', 'unknown')
        if service_status == 'healthy':
            sys.exit(0)
        elif service_status == 'degraded':
            sys.exit(1)
        else:
            sys.exit(2)
            
    except Exception as e:
        print(f"Health check failed: {e}")
        sys.exit(3)
    finally:
        close_database_manager()

def export_metrics(output_file: str):
    """Export metrics to JSON file."""
    try:
        health_checker = get_health_checker()
        health_data = health_checker.get_detailed_status()
        
        # Add export timestamp
        health_data['export_timestamp'] = datetime.now().isoformat()
        
        with open(output_file, 'w') as f:
            json.dump(health_data, f, indent=2, default=str)
        
        print(f"Metrics exported to {output_file}")
        
    except Exception as e:
        print(f"Failed to export metrics: {e}")
        sys.exit(1)
    finally:
        close_database_manager()

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='MCP-MEM0 Database Monitor')
    parser.add_argument('--continuous', '-c', action='store_true',
                       help='Run continuous monitoring')
    parser.add_argument('--interval', '-i', type=int, default=30,
                       help='Monitoring interval in seconds (default: 30)')
    parser.add_argument('--export', '-e', type=str,
                       help='Export metrics to JSON file')
    parser.add_argument('--json', '-j', action='store_true',
                       help='Output in JSON format')
    
    args = parser.parse_args()
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    if args.export:
        export_metrics(args.export)
    elif args.continuous:
        monitor_continuous(args.interval)
    else:
        if args.json:
            try:
                health_checker = get_health_checker()
                health_data = health_checker.get_detailed_status()
                print(json.dumps(health_data, indent=2, default=str))
            except Exception as e:
                print(json.dumps({"error": str(e)}, indent=2))
            finally:
                close_database_manager()
        else:
            monitor_single()

if __name__ == '__main__':
    main()
