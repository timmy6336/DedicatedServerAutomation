"""
Logging utilities — copied from the original utils/logging_utils.py.
Path references updated for the new src/core/ location.
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

LOG_DIRECTORY = "logs"
LOG_FILE_PREFIX = "server_automation"
MAX_LOG_SIZE_MB = 10
MAX_LOG_FILES = 5
LOG_FORMAT = "%(asctime)s [%(levelname)8s] %(name)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class EnhancedLogger:
    """Enhanced logger with detailed system context and error tracking."""

    def __init__(self, name: str, log_dir: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        if self.logger.handlers:
            return

        if log_dir is None:
            # Go up from src/core → src → project root
            project_root = Path(__file__).parent.parent.parent
            log_dir = project_root / LOG_DIRECTORY
        else:
            log_dir = Path(log_dir)

        log_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"{LOG_FILE_PREFIX}_{timestamp}.log"

        formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        self.logger.info(f"Enhanced logging initialized — Log file: {log_file}")
        self._log_system_info()

    def _log_system_info(self):
        try:
            self.logger.info("=" * 60)
            self.logger.info("SYSTEM INFORMATION")
            self.logger.info("=" * 60)
            self.logger.info(f"Platform: {platform.platform()}")
            self.logger.info(f"System: {platform.system()} {platform.release()}")
            self.logger.info(f"Python: {platform.python_version()}")

            memory = psutil.virtual_memory()
            self.logger.info(f"Total RAM: {memory.total / (1024**3):.2f} GB")
            self.logger.info(f"Available RAM: {memory.available / (1024**3):.2f} GB")

            for disk in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(disk.mountpoint)
                    free_gb = usage.free / (1024**3)
                    total_gb = usage.total / (1024**3)
                    self.logger.info(
                        f"  {disk.device} - {free_gb:.2f}GB free / {total_gb:.2f}GB total"
                    )
                except PermissionError:
                    self.logger.warning(f"  {disk.device} - Access denied")

            self.logger.info("=" * 60)
        except Exception as e:
            self.logger.warning(f"Could not gather system info: {e}")

    def log_operation_start(self, operation: str, details: Optional[Dict[str, Any]] = None):
        self.logger.info(f"Starting operation: {operation}")
        if details:
            for k, v in details.items():
                self.logger.info(f"  {k}: {v}")

    def log_operation_success(self, operation: str, duration: Optional[float] = None,
                              details: Optional[Dict[str, Any]] = None):
        msg = f"Operation completed: {operation}"
        if duration:
            msg += f" (took {duration:.2f}s)"
        self.logger.info(msg)
        if details:
            for k, v in details.items():
                self.logger.info(f"  {k}: {v}")

    def log_operation_failure(self, operation: str, error: Exception,
                              duration: Optional[float] = None,
                              context: Optional[Dict[str, Any]] = None):
        msg = f"Operation failed: {operation}"
        if duration:
            msg += f" (failed after {duration:.2f}s)"
        self.logger.error(msg)
        self.logger.error(f"Error type: {type(error).__name__}")
        self.logger.error(f"Error message: {str(error)}")
        if context:
            for k, v in context.items():
                self.logger.error(f"  {k}: {v}")
        for line in traceback.format_exc().splitlines():
            self.logger.error(f"  {line}")

    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def critical(self, message: str):
        self.logger.critical(message)


class OperationTimer:
    """Context manager for timing operations."""

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
    return EnhancedLogger(name)


def cleanup_old_logs(log_dir: Optional[str] = None, max_files: int = MAX_LOG_FILES):
    if log_dir is None:
        project_root = Path(__file__).parent.parent.parent
        log_dir = project_root / LOG_DIRECTORY
    else:
        log_dir = Path(log_dir)

    if not log_dir.exists():
        return

    log_files = sorted(
        log_dir.glob(f"{LOG_FILE_PREFIX}_*.log"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )
    for old_file in log_files[max_files:]:
        try:
            old_file.unlink()
        except OSError:
            pass
