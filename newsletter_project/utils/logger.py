import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """Provides a standard logger format for the newsletter project."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")
        
        # Console Handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        # File Handler
        try:
            fh = logging.FileHandler("newsletter_pipeline.log", encoding="utf-8")
            fh.setFormatter(formatter)
            logger.addHandler(fh)
        except Exception as e:
            # Fallback for permission errors
            pass 
            
    return logger
