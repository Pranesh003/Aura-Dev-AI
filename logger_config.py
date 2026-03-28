import logging
import os
import queue
import contextvars
from logging.handlers import RotatingFileHandler

log_queue = queue.Queue()
job_id_var = contextvars.ContextVar('job_id', default='global')

def set_job_id(job_id: str):
    job_id_var.set(job_id)

class QueueHandler(logging.Handler):
    def emit(self, record):
        try:
            msg = self.format(record)
            job_id = job_id_var.get()
            log_queue.put_nowait((job_id, msg))
        except Exception:
            self.handleError(record)

def get_logger(name="aura_engine"):
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
        
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        # File handler
        log_file = os.path.join(log_dir, "aura_engine.log")
        file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5, encoding="utf-8")
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(console_handler)
        
        # Queue handler for WebSocket streaming
        queue_handler = QueueHandler()
        queue_handler.setFormatter(logging.Formatter('[%(name)s] %(message)s'))
        logger.addHandler(queue_handler)
        
    return logger
