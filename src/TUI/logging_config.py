import os
import logging
from datetime import datetime
from pathlib import Path

class SingletonLogger:
    _instance = None
    _initialized = False

    @classmethod
    def setup_logger(cls):
        if cls._initialized:
            return logging.getLogger('tui')
            
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        logs_dir = os.path.join(project_root, 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        log_file = os.path.join(logs_dir, f"tui_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        
        # Create a logger with a unique name
        logger = logging.getLogger('tui')
        logger.setLevel(logging.DEBUG)
        
        # Prevent adding handlers multiple times
        if not logger.handlers:
            # File handler
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)  # Less verbose for console
            console_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
        
        # Suppress asyncio and other library logging
        logging.getLogger('asyncio').setLevel(logging.WARNING)
        logging.getLogger('textual').setLevel(logging.WARNING)
        
        cls._initialized = True
        return logger

def get_logger(name: str = None):
    base_logger = SingletonLogger.setup_logger()
    if name:
        return base_logger.getChild(name)
    return base_logger