"""
Enhanced Logging Utilities for Dedicated Server Automation

This module provides comprehensive logging functionality for debugging installation
and setup issues. It creates detailed logs with timestamps, error context, and
system information to help diagnose problems.

Features:
- Timestamped log entries with severity levels
- Automatic log file rotation to prevent disk space issues
- System information capture for debugging
- Error context preservation with full stack traces
- Performance timing for operations
- Network and disk space monitoring
"""

import os
import sys
import logging
import traceback
import time
import platform
import psutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# ================== LOGGING CONSTANTS ==================
LOG_DIRECTORY = "logs"                   # Directory name for log files
LOG_FILE_PREFIX = "server_automation"    # Prefix for log file names
MAX_LOG_SIZE_MB = 10                     # Maximum size per log file in MB
MAX_LOG_FILES = 5                        # Maximum number of log files to keep
LOG_FORMAT = "%(asctime)s [%(levelname)8s] %(name)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

class EnhancedLogger:
    """Enhanced logger with detailed system context and error tracking"""
    
    def __init__(self, name: str, log_dir: Optional[str] = None):
        """
        Initialize enhanced logger with file and console output
        
        Args:
            name: Logger name (usually module or component name)
            log_dir: Custom log directory (defaults to logs/ in project root)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers if logger already exists
        if self.logger.handlers:
            return
            
        # Determine log directory
        if log_dir is None:
            # Get project root directory (go up from src/utils)
            project_root = Path(__file__).parent.parent.parent
            log_dir = project_root / LOG_DIRECTORY
        else:
            log_dir = Path(log_dir)
            
        # Create log directory if it doesn't exist
        log_dir.mkdir(exist_ok=True)
        
        # Create log file path with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"{LOG_FILE_PREFIX}_{timestamp}.log"
        
        # Set up formatters
        formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
        
        # File handler with rotation
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Console handler for immediate feedback
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Log initialization
        self.logger.info(f"Enhanced logging initialized - Log file: {log_file}")
        self._log_system_info()
    
    def _log_system_info(self):
        """Log detailed system information for debugging context"""
        try:
            # System information
            self.logger.info("=" * 60)
            self.logger.info("SYSTEM INFORMATION")
            self.logger.info("=" * 60)
            self.logger.info(f"Platform: {platform.platform()}")
            self.logger.info(f"System: {platform.system()} {platform.release()}")
            self.logger.info(f"Machine: {platform.machine()}")
            self.logger.info(f"Processor: {platform.processor()}")
            self.logger.info(f"Python: {platform.python_version()} ({platform.python_implementation()})")
            
            # Memory information
            memory = psutil.virtual_memory()
            self.logger.info(f"Total RAM: {memory.total / (1024**3):.2f} GB")
            self.logger.info(f"Available RAM: {memory.available / (1024**3):.2f} GB")
            self.logger.info(f"RAM Usage: {memory.percent}%")
            
            # Disk information
            self.logger.info("Disk Space Information:")
            for disk in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(disk.mountpoint)
                    free_gb = usage.free / (1024**3)
                    total_gb = usage.total / (1024**3)
                    used_percent = (usage.used / usage.total) * 100
                    self.logger.info(f"  {disk.device} - {free_gb:.2f}GB free / {total_gb:.2f}GB total ({used_percent:.1f}% used)")
                except PermissionError:
                    self.logger.warning(f"  {disk.device} - Access denied")
            
            self.logger.info("=" * 60)
            
        except Exception as e:
            self.logger.warning(f"Could not gather complete system information: {e}")
    
    def log_operation_start(self, operation: str, details: Optional[Dict[str, Any]] = None):
        """Log the start of an operation with context"""
        self.logger.info(f"🚀 Starting operation: {operation}")
        if details:
            for key, value in details.items():
                self.logger.info(f"  {key}: {value}")
    
    def log_operation_success(self, operation: str, duration: Optional[float] = None, details: Optional[Dict[str, Any]] = None):
        """Log successful completion of an operation"""
        message = f"✅ Operation completed successfully: {operation}"
        if duration:
            message += f" (took {duration:.2f}s)"
        self.logger.info(message)
        if details:
            for key, value in details.items():
                self.logger.info(f"  {key}: {value}")
    
    def log_operation_failure(self, operation: str, error: Exception, duration: Optional[float] = None, context: Optional[Dict[str, Any]] = None):
        """Log operation failure with full context and stack trace"""
        message = f"❌ Operation failed: {operation}"
        if duration:
            message += f" (failed after {duration:.2f}s)"
        
        self.logger.error(message)
        self.logger.error(f"Error type: {type(error).__name__}")
        self.logger.error(f"Error message: {str(error)}")
        
        # Log context if provided
        if context:
            self.logger.error("Error context:")
            for key, value in context.items():
                self.logger.error(f"  {key}: {value}")
        
        # Log full stack trace
        self.logger.error("Full stack trace:")
        for line in traceback.format_exc().splitlines():
            self.logger.error(f"  {line}")
    
    def log_subprocess_output(self, command: str, stdout: str, stderr: str, exit_code: int):
        """Log detailed subprocess execution results"""
        self.logger.info(f"Subprocess command: {command}")
        self.logger.info(f"Exit code: {exit_code}")
        
        if stdout:
            self.logger.info("STDOUT:")
            for line in stdout.splitlines():
                self.logger.info(f"  {line}")
        
        if stderr:
            if exit_code == 0:
                self.logger.warning("STDERR (non-fatal):")
                for line in stderr.splitlines():
                    self.logger.warning(f"  {line}")
            else:
                self.logger.error("STDERR:")
                for line in stderr.splitlines():
                    self.logger.error(f"  {line}")
    
    def log_network_diagnostics(self):
        """Log network connectivity diagnostics"""
        self.logger.info("Network Diagnostics:")
        
        # Check internet connectivity
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            self.logger.info("  ✅ Internet connectivity: OK")
        except OSError:
            self.logger.error("  ❌ Internet connectivity: FAILED")
        
        # Check Steam connectivity
        try:
            import socket
            socket.create_connection(("steamcommunity.com", 80), timeout=3)
            self.logger.info("  ✅ Steam connectivity: OK")
        except OSError:
            self.logger.error("  ❌ Steam connectivity: FAILED")
    
    def log_file_operation(self, operation: str, file_path: str, success: bool, error: Optional[str] = None, file_size: Optional[int] = None):
        """Log file operations with detailed information"""
        if success:
            message = f"✅ File operation successful: {operation} - {file_path}"
            if file_size is not None:
                message += f" ({file_size / (1024*1024):.2f} MB)"
            self.logger.info(message)
        else:
            self.logger.error(f"❌ File operation failed: {operation} - {file_path}")
            if error:
                self.logger.error(f"  Error: {error}")
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(message)

class OperationTimer:
    """Context manager for timing operations"""
    
    def __init__(self, logger: EnhancedLogger, operation_name: str):
        self.logger = logger
        self.operation_name = operation_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.log_operation_start(self.operation_name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if exc_type is None:
            self.logger.log_operation_success(self.operation_name, duration)
        else:
            self.logger.log_operation_failure(self.operation_name, exc_val, duration)

def get_logger(name: str) -> EnhancedLogger:
    """Get an enhanced logger instance"""
    return EnhancedLogger(name)

def cleanup_old_logs(log_dir: Optional[str] = None, max_files: int = MAX_LOG_FILES):
    """Clean up old log files to prevent disk space issues"""
    if log_dir is None:
        project_root = Path(__file__).parent.parent.parent
        log_dir = project_root / LOG_DIRECTORY
    else:
        log_dir = Path(log_dir)
    
    if not log_dir.exists():
        return
    
    # Get all log files sorted by modification time (newest first)
    log_files = sorted(
        log_dir.glob(f"{LOG_FILE_PREFIX}_*.log"),
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )
    
    # Remove excess log files
    for old_file in log_files[max_files:]:
        try:
            old_file.unlink()
        except OSError:
            pass  # Ignore errors when cleaning up
