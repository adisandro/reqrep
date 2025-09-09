import logging
from logging import StreamHandler


def setup_logger(verbose=True, logfile=None):
    logger = logging.getLogger("gp_logger")
    if verbose:
        logger.addHandler(StreamHandler())
        logger.setLevel(logging.INFO)
        if logfile:
            fh = logging.FileHandler(logfile)
            fh.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(message)s')
            fh.setFormatter(formatter)
            logger.addHandler(fh)
    else:
        logger.addHandler(logging.NullHandler())

    return logger

