import logging
import sys
from typing import Optional

def setup_logger(name: str = "WindowManager", level: int = logging.INFO, log_file: Optional[str] = None) -> logging.Logger:
    """
    Sets up a logger with the specified name, level, and optional file output.
    
    Args:
        name: The name of the logger.
        level: The logging level.
        log_file: Optional path to a log file.
        
    Returns:
        A configured logging.Logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if logger.hasHandlers():
        return logger
        
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
    return logger
