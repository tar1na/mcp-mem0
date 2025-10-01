"""
Logging configuration for mcp-mem0 server.
Respects DEBUG and LOG_LEVEL environment variables.
"""

import logging
import sys
from config import DEBUG, LOG_LEVEL

def setup_logging():
    """Setup logging configuration based on environment variables."""
    
    # Set log level based on environment variable
    log_level = getattr(logging, LOG_LEVEL, logging.INFO)
    
    # Configure logging format
    if DEBUG:
        # Debug format with more details
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    else:
        # Production format - cleaner
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific logger levels
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('mem0').setLevel(logging.INFO)
    logging.getLogger('database_manager').setLevel(logging.INFO)
    
    return logging.getLogger('mcp-mem0')

def debug_log(message: str):
    """Log debug message only if DEBUG is enabled."""
    if DEBUG:
        logger = logging.getLogger('mcp-mem0')
        logger.debug(message)

def info_log(message: str):
    """Log info message."""
    logger = logging.getLogger('mcp-mem0')
    logger.info(message)

def warning_log(message: str):
    """Log warning message."""
    logger = logging.getLogger('mcp-mem0')
    logger.warning(message)

def error_log(message: str):
    """Log error message."""
    logger = logging.getLogger('mcp-mem0')
    logger.error(message)
