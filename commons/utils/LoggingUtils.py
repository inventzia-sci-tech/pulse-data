import logging
import logging.handlers
import os
from logging.handlers import TimedRotatingFileHandler
# ---------------------------------------
# Logging instantiation utility
# ---------------------------------------
def instantiate_logging(logfilename: str = None,
                        rotating: bool = False,
                        loglevel=logging.INFO,
                        log_id: str = None):
    """
    Configure logging with optional file output and rotation.

    Args:
        logfilename: Path to log file. If None, only console logging is used.
        rotating: If True, use TimedRotatingFileHandler (midnight rotation, 5 backups).
                 If False, use standard FileHandler.
        loglevel: Logging level (default: logging.INFO)
        log_id: Logger identifier. If None, returns the root logger.

    Returns:
        logging.Logger: Configured logger instance
    """
    if logfilename is not None:
        if rotating:
            handler = logging.handlers.TimedRotatingFileHandler(
                logfilename, "midnight", backupCount=5
            )
            handler.suffix = "%Y%m%d"
            log_handlers = [handler, logging.StreamHandler()]
        else:
            log_handlers = [logging.FileHandler(logfilename), logging.StreamHandler()]
    else:
        log_handlers = [logging.StreamHandler()]

    logging.basicConfig(
        level=loglevel,
        format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
        handlers=log_handlers,
    )
    # Get and return the logger with the specified ID
    logger = logging.getLogger(log_id) if log_id else logging.getLogger()
    logger.setLevel(loglevel)
    return logger