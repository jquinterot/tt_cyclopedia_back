import logging
import re
import os
from typing import Any, Dict

class SensitiveDataFilter(logging.Filter):
    """
    Logging filter that masks sensitive data in log messages.
    
    This filter automatically redacts passwords, tokens, emails,
    and other sensitive information from log output.
    """
    
    # Patterns for sensitive data
    SENSITIVE_PATTERNS = [
        # Passwords
        (re.compile(r'(password["\']?\s*[:=]\s*["\']?)([^"\'\s,\}]+)', re.IGNORECASE), r'\1[REDACTED]'),
        (re.compile(r'(passwd["\']?\s*[:=]\s*["\']?)([^"\'\s,\}]+)', re.IGNORECASE), r'\1[REDACTED]'),
        (re.compile(r'(pwd["\']?\s*[:=]\s*["\']?)([^"\'\s,\}]+)', re.IGNORECASE), r'\1[REDACTED]'),
        
        # JWT Tokens
        (re.compile(r'(Bearer\s+)([A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+)', re.IGNORECASE), r'\1[REDACTED_TOKEN]'),
        (re.compile(r'(jwt["\']?\s*[:=]\s*["\']?)([^"\'\s,\}]+)', re.IGNORECASE), r'\1[REDACTED]'),
        (re.compile(r'(token["\']?\s*[:=]\s*["\']?)([^"\'\s,\}]+)', re.IGNORECASE), r'\1[REDACTED]'),
        
        # API Keys / Secrets
        (re.compile(r'(api[_-]?key["\']?\s*[:=]\s*["\']?)([^"\'\s,\}]+)', re.IGNORECASE), r'\1[REDACTED]'),
        (re.compile(r'(api[_-]?secret["\']?\s*[:=]\s*["\']?)([^"\'\s,\}]+)', re.IGNORECASE), r'\1[REDACTED]'),
        (re.compile(r'(secret["\']?\s*[:=]\s*["\']?)([^"\'\s,\}]+)', re.IGNORECASE), r'\1[REDACTED]'),
        (re.compile(r'(access[_-]?key["\']?\s*[:=]\s*["\']?)([^"\'\s,\}]+)', re.IGNORECASE), r'\1[REDACTED]'),
        
        # Email addresses
        (re.compile(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'), '[EMAIL_REDACTED]'),
        
        # Database connection strings
        (re.compile(r'(postgresql://[^:]+:)[^@]+(@.+)'), r'\1[REDACTED]\2'),
        (re.compile(r'(mysql://[^:]+:)[^@]+(@.+)'), r'\1[REDACTED]\2'),
        (re.compile(r'(mongodb(\+srv)?://[^:]+:)[^@]+(@.+)'), r'\1[REDACTED]\2'),
        
        # Authorization headers
        (re.compile(r'(Authorization["\']?\s*[:=]\s*["\']?)([^"\'\s,\}]+)', re.IGNORECASE), r'\1[REDACTED]'),
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter and mask sensitive data in log messages.
        
        Args:
            record: The log record to filter
            
        Returns:
            True to allow the log message, False to drop it
        """
        if record.msg:
            # Convert to string if it's not
            message = str(record.msg)
            
            # Apply all patterns
            for pattern, replacement in self.SENSITIVE_PATTERNS:
                message = pattern.sub(replacement, message)
            
            # Update the record with masked message
            record.msg = message
        
        # Also mask args if present
        if record.args:
            masked_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    for pattern, replacement in self.SENSITIVE_PATTERNS:
                        arg = pattern.sub(replacement, arg)
                masked_args.append(arg)
            record.args = tuple(masked_args)
        
        return True


def setup_logging(log_level: str = None) -> None:
    """
    Configure application logging with sensitive data filtering.
    
    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                   Defaults to environment variable LOG_LEVEL or INFO
    """
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO")
    
    # Get existing handlers
    root_logger = logging.getLogger()
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add sensitive data filter
    console_handler.addFilter(SensitiveDataFilter())
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: The name for the logger (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)