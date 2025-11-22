import logging
import sys


def setup_logging(level=logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    fmt = logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(fmt)

    if not logger.handlers:
        logger.addHandler(handler)
