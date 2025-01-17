import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional
import os
from logging.handlers import RotatingFileHandler

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # File handler with rotation
        file_handler = RotatingFileHandler(
            'logs/wallet.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatters and add it to the handlers
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        file_formatter = logging.Formatter(log_format)
        console_formatter = logging.Formatter(log_format)
        
        file_handler.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)
        
        # Add the handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def _format_message(
        self,
        message: str,
        extra: Optional[Dict[str, Any]] = None
    ) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": message
        }
        if extra:
            log_data.update(extra)
        return json.dumps(log_data)
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        self.logger.info(self._format_message(message, extra))
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        self.logger.warning(self._format_message(message, extra))
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info=True):
        self.logger.error(self._format_message(message, extra), exc_info=exc_info)
    
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info=True):
        self.logger.critical(self._format_message(message, extra), exc_info=exc_info)

# Create logger instance
logger = StructuredLogger('wallet_backend') 