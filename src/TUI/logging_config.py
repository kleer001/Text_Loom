import os
import logging
from datetime import datetime
from pathlib import Path

class SingletonLogger:
    _instance = None
    _initialized = False

    LOGGING_LEVELS = {
        3: [logging.INFO, logging.DEBUG, logging.ERROR],
        2: [logging.DEBUG, logging.ERROR],
        1: [logging.ERROR],
        0: []
    }

    @classmethod
    def setup_logger(cls, level: int = 3):
        if cls._initialized:
            return logging.getLogger('tui')
            
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        logs_dir = os.path.join(project_root, 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        log_file = os.path.join(logs_dir, f"tui_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        
        logger = logging.getLogger('tui')
        logger.setLevel(logging.DEBUG)  
        
        if not logger.handlers:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            
        logging.getLogger('asyncio').setLevel(logging.WARNING)
        logging.getLogger('textual').setLevel(logging.WARNING)
        
        cls._initialized = True
        return logger

class LevelFilter(logging.Filter):
    def __init__(self, allowed_levels):
        super().__init__()
        self.allowed_levels = allowed_levels

    def filter(self, record):
        return record.levelno in self.allowed_levels

def get_logger(name: str = None, level: int = 3):
    if level not in SingletonLogger.LOGGING_LEVELS:
        level = 3
        
    logger = SingletonLogger.setup_logger()
    
    if name:
        logger = logger.getChild(name)
    
    logger.filters = []
    allowed_levels = SingletonLogger.LOGGING_LEVELS[level]
    
    if not allowed_levels:
        logger.addFilter(lambda record: False)
    else:
        logger.addFilter(LevelFilter(allowed_levels))
    
    return logger