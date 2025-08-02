import logging
from logging.handlers import RotatingFileHandler

def setup_security_logger():
    """
    Sets up a dedicated logger for security-related events.
    """
    logger = logging.getLogger("auth_security")
    logger.setLevel(logging.INFO)

    # Avoid adding handlers if they already exist
    if not logger.handlers:
        # Create a rotating file handler
        handler = RotatingFileHandler(
            "auth_events.log",
            maxBytes=1024 * 1024 * 5,  # 5 MB
            backupCount=5
        )

        # Create a formatter and set it for the handler
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(handler)

    return logger

security_logger = setup_security_logger()
