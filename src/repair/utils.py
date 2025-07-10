import logging

def setup_logger(logfile="repair.log"):
    logger = logging.getLogger("gp_logger")
    logger.setLevel(logging.INFO)

    if not logger.handlers:  # Prevent duplicate handlers
        fh = logging.FileHandler(logfile)
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger

