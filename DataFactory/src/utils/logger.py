import logging
import sys
import os
from config import cfg

class CleanFormatter(logging.Formatter):
    """
    Custom formatter to add colors to console output for better readability.
    """
    grey = "\x1b[38;20m"
    blue = "\x1b[34;20m"
    green = "\x1b[32;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    
    # Simple format: Time | Level | Message
    format_str = "%(asctime)s | %(levelname)-8s | %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format_str + reset,
        logging.INFO: green + format_str + reset,
        logging.WARNING: yellow + format_str + reset,
        logging.ERROR: red + format_str + reset,
        logging.CRITICAL: bold_red + format_str + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%H:%M:%S")
        return formatter.format(record)

_setup_done = False

def setup_logging():
    """
    Configures the root logger. Should be called once at the application entry point.
    """
    global _setup_done
    if _setup_done:
        return

    # Get level from config, default to INFO
    level_str = cfg.get("logging.level", "INFO").upper()
    level = getattr(logging, level_str, logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers to avoid duplicates if re-initialized
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(CleanFormatter())
    root_logger.addHandler(console_handler)

    # File Handler (Optional)
    log_file = cfg.get("logging.file")
    if log_file:
        try:
            log_path = cfg.get_abs_path("logging.file")
            # If get_abs_path returns None or same string if not found in config, handle it
            if not log_path: 
                 # Fallback if key exists but is empty, or construct manually if needed
                 # But cfg.get("logging.file") returned something, so...
                 if not os.path.isabs(log_file):
                     log_path = os.path.join(cfg.project_root, log_file)
                 else:
                     log_path = log_file

            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            
            file_handler = logging.FileHandler(log_path, encoding='utf-8')
            # More detailed format for file logs
            file_formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s", 
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            print(f"Failed to setup file logging: {e}")

    _setup_done = True

def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger instance with the given name.
    Ensures logging is set up.
    """
    if not _setup_done:
        setup_logging()
    return logging.getLogger(name)
