"""
Logging utility for BitWipers.
Provides structured logging with multiple output formats and security considerations.
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path


class Logger:
    """Secure logging utility for BitWipers."""
    
    def __init__(self, 
                 name: str,
                 log_level: str = "INFO",
                 log_file: Optional[str] = None,
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5,
                 enable_console: bool = True):
        """
        Initialize logger.
        
        Args:
            name: Logger name
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Path to log file (optional)
            max_file_size: Maximum log file size in bytes
            backup_count: Number of backup files to keep
            enable_console: Whether to enable console logging
        """
        self.name = name
        self.logger = logging.getLogger(name)
        
        # Set log level
        level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger.setLevel(level)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create formatter
        formatter = self._create_formatter()
        
        # Add console handler if enabled
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            console_handler.setLevel(level)
            self.logger.addHandler(console_handler)
        
        # Add file handler if log file specified
        if log_file:
            self._add_file_handler(log_file, formatter, max_file_size, backup_count)
        
        # Prevent log messages from being processed by parent loggers
        self.logger.propagate = False
    
    def _create_formatter(self) -> logging.Formatter:
        """Create log formatter with security considerations."""
        format_string = (
            "[%(asctime)s] %(levelname)-8s %(name)s:%(lineno)d - %(message)s"
        )
        
        formatter = logging.Formatter(
            format_string,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        return formatter
    
    def _add_file_handler(self, 
                         log_file: str,
                         formatter: logging.Formatter,
                         max_file_size: int,
                         backup_count: int):
        """Add rotating file handler."""
        try:
            # Create log directory if it doesn't exist
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Use rotating file handler to prevent logs from growing too large
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            
            file_handler.setFormatter(formatter)
            file_handler.setLevel(self.logger.level)
            
            self.logger.addHandler(file_handler)
            
        except Exception as e:
            # If file logging fails, log to console
            self.logger.warning(f"Could not create file handler for {log_file}: {e}")
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self._log(logging.CRITICAL, message, **kwargs)
    
    def _log(self, level: int, message: str, **kwargs):
        """
        Internal logging method with security sanitization.
        
        Args:
            level: Logging level
            message: Log message
            **kwargs: Additional context data
        """
        # Sanitize message to prevent log injection
        sanitized_message = self._sanitize_message(message)
        
        # Add context if provided
        if kwargs:
            sanitized_kwargs = self._sanitize_context(kwargs)
            context_str = " | ".join([f"{k}={v}" for k, v in sanitized_kwargs.items()])
            sanitized_message = f"{sanitized_message} | {context_str}"
        
        # Log the message
        self.logger.log(level, sanitized_message)
    
    def _sanitize_message(self, message: str) -> str:
        """
        Sanitize log message to prevent log injection attacks.
        
        Args:
            message: Raw log message
            
        Returns:
            str: Sanitized message
        """
        if not isinstance(message, str):
            message = str(message)
        
        # Remove/replace potentially dangerous characters
        sanitized = message.replace('\n', '\\n').replace('\r', '\\r')
        sanitized = sanitized.replace('\t', '\\t')
        
        # Truncate very long messages to prevent log spam
        if len(sanitized) > 1000:
            sanitized = sanitized[:997] + "..."
        
        return sanitized
    
    def _sanitize_context(self, context: Dict[str, Any]) -> Dict[str, str]:
        """
        Sanitize context data to prevent sensitive information leakage.
        
        Args:
            context: Context data dictionary
            
        Returns:
            Dict[str, str]: Sanitized context data
        """
        sensitive_keys = {
            'password', 'passwd', 'pwd', 'secret', 'key', 'token',
            'auth', 'credential', 'private', 'hash', 'signature'
        }
        
        sanitized = {}
        
        for key, value in context.items():
            # Sanitize key name
            clean_key = str(key).lower().replace(' ', '_')
            
            # Check if key contains sensitive information
            if any(sensitive in clean_key for sensitive in sensitive_keys):
                sanitized[clean_key] = "[REDACTED]"
            else:
                # Convert value to string and sanitize
                str_value = str(value)
                sanitized_value = self._sanitize_message(str_value)
                
                # Truncate long values
                if len(sanitized_value) > 100:
                    sanitized_value = sanitized_value[:97] + "..."
                
                sanitized[clean_key] = sanitized_value
        
        return sanitized
    
    def log_wipe_start(self, device_path: str, pattern: str, **kwargs):
        """Log wipe operation start."""
        self.info(
            f"Wipe operation started",
            device_path=self._redact_sensitive_path(device_path),
            pattern=pattern,
            **kwargs
        )
    
    def log_wipe_progress(self, device_path: str, progress: float, **kwargs):
        """Log wipe operation progress."""
        self.debug(
            f"Wipe progress",
            device_path=self._redact_sensitive_path(device_path),
            progress_percent=f"{progress:.1f}%",
            **kwargs
        )
    
    def log_wipe_complete(self, device_path: str, duration: float, status: str, **kwargs):
        """Log wipe operation completion."""
        self.info(
            f"Wipe operation completed",
            device_path=self._redact_sensitive_path(device_path),
            duration_seconds=f"{duration:.2f}",
            status=status,
            **kwargs
        )
    
    def log_certificate_generated(self, certificate_id: str, **kwargs):
        """Log certificate generation."""
        self.info(
            f"Certificate generated",
            certificate_id=certificate_id,
            **kwargs
        )
    
    def log_security_event(self, event_type: str, description: str, **kwargs):
        """Log security-related events."""
        self.warning(
            f"Security event: {event_type}",
            description=description,
            **kwargs
        )
    
    def _redact_sensitive_path(self, path: str) -> str:
        """
        Redact potentially sensitive parts of file paths.
        
        Args:
            path: File or device path
            
        Returns:
            str: Redacted path
        """
        if not path:
            return "[EMPTY_PATH]"
        
        # Keep only the device/file name, not the full path
        path_obj = Path(path)
        return f".../{path_obj.name}"
    
    def create_audit_logger(self, audit_file: str) -> 'Logger':
        """
        Create a separate audit logger for compliance and security auditing.
        
        Args:
            audit_file: Path to audit log file
            
        Returns:
            Logger: Audit logger instance
        """
        audit_logger = Logger(
            name=f"{self.name}_audit",
            log_level="INFO",
            log_file=audit_file,
            max_file_size=50 * 1024 * 1024,  # 50MB for audit logs
            backup_count=10,
            enable_console=False  # Audit logs usually don't go to console
        )
        
        return audit_logger
    
    def get_log_stats(self) -> Dict[str, Any]:
        """
        Get logging statistics.
        
        Returns:
            Dict with logging statistics
        """
        stats = {
            'logger_name': self.name,
            'log_level': logging.getLevelName(self.logger.level),
            'handlers_count': len(self.logger.handlers),
            'handlers': []
        }
        
        for handler in self.logger.handlers:
            handler_info = {
                'type': type(handler).__name__,
                'level': logging.getLevelName(handler.level)
            }
            
            if hasattr(handler, 'baseFilename'):
                handler_info['file'] = handler.baseFilename
                
                # Get file size if file exists
                if os.path.exists(handler.baseFilename):
                    handler_info['file_size'] = os.path.getsize(handler.baseFilename)
            
            stats['handlers'].append(handler_info)
        
        return stats


# Global logger instance for convenience
_default_logger: Optional[Logger] = None


def get_logger(name: str = "BitWipers") -> Logger:
    """
    Get or create default logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger: Logger instance
    """
    global _default_logger
    
    if _default_logger is None:
        # Create default log directory
        log_dir = Path.home() / ".bitwipers" / "logs"
        log_file = log_dir / f"{name.lower()}.log"
        
        _default_logger = Logger(
            name=name,
            log_file=str(log_file),
            enable_console=True
        )
    
    return _default_logger


def setup_logging(log_level: str = "INFO", 
                 log_file: Optional[str] = None,
                 enable_console: bool = True) -> Logger:
    """
    Setup application-wide logging configuration.
    
    Args:
        log_level: Logging level
        log_file: Path to log file
        enable_console: Whether to enable console logging
        
    Returns:
        Logger: Configured logger instance
    """
    global _default_logger
    
    _default_logger = Logger(
        name="BitWipers",
        log_level=log_level,
        log_file=log_file,
        enable_console=enable_console
    )
    
    return _default_logger
