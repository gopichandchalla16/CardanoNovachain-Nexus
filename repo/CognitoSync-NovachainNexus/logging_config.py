import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(log_level=logging.INFO):
    """
    Configure application-wide logging
    """
    # Create logs directory if it doesn't exist
    log_directory = "logs"
    os.makedirs(log_directory, exist_ok=True)
    log_file = os.path.join(log_directory, "app.log")
    
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Set up rotating file handler (10 MB per file, keep 5 backup files)
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5
    )
    file_handler.setFormatter(file_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Add the file handler (checking for duplicates is often good practice)
    if not any(isinstance(handler, RotatingFileHandler) for handler in root_logger.handlers):
        root_logger.addHandler(file_handler)
    
    return root_logger

def get_logger(name):
    """
    Get a logger for a specific module
    """
    return logging.getLogger(name)