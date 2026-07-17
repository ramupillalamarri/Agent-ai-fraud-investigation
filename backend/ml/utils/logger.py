"""Structured logging configuration utility for the ML module."""

import logging
import sys
from typing import Optional

def get_ml_logger(name: str, log_level: Optional[int] = None) -> logging.Logger:
    """Configures and returns a logger for the ML module.
    
    Args:
        name: Name of the logger, typically __name__.
        log_level: Optional logging level override (e.g. logging.DEBUG).
        
    Returns:
        logging.Logger: A configured logger instance.
    """
    logger = logging.getLogger(name)
    
    # If the logger already has handlers, do not add more (prevents duplicate logs)
    if logger.handlers:
        return logger
        
    if log_level is None:
        log_level = logging.INFO
        
    logger.setLevel(log_level)
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Format
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s:%(filename)s:%(lineno)d]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    # TODO: Add file logging handler configured from PathConfig in config.py
    
    return logger
