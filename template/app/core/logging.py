import logging
import sys

from app.core.config import settings

def setup_logging() -> None:
    """
    Configure application logging.
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Silence noisy third-party libraries if needed
    logging.getLogger("httpx").setLevel(logging.WARNING)
