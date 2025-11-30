import os
import logging
from logging.handlers import RotatingFileHandler
import sys # Added for StreamHandler

def setup_logging(log_level=logging.INFO):
    """
    Configure application-wide logging
    
    Args:
        log_level: The minimum log level to capture (default: INFO)
    
    Returns:
        logger: Configured root logger instance
    """
    # Create logs directory if it doesn't exist
    log_directory = "logs"
    os.makedirs(log_directory, exist_ok=True)
    log_file = os.path.join(log_directory, "app.log")
    
    # Create formatter for consistent log formatting
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Set up rotating file handler (10 MB per file, keep 5 backup files)
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5
    )
    file_handler.setFormatter(file_formatter)

    # Console Handler for stdout (important for FastAPI/Uvicorn logging)
    console_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove any existing handlers to prevent duplicates
    for handler in root_logger.handlers[:]:
        if isinstance(handler, (logging.StreamHandler, RotatingFileHandler)):
            root_logger.removeHandler(handler)
    
    # Add the file and console handler
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler) 
    
    return root_logger

# FIX: Added get_logger function to resolve 'Import "logging_config" could not be resolved'
# due to missing 'get_logger' export
def get_logger(name: str):
    """
    Returns a logger instance for a given module name.
    """
    return logging.getLogger(name)
