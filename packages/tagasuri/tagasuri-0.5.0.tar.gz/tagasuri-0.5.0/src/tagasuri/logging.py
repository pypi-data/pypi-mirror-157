import logging


def create_log_handler(fname):
    """ Log to different files
    """
    logger = logging.getLogger(name=fname)
    logger.setLevel(logging.DEBUG)
    fileHandler = logging.FileHandler(f'{fname}.log', mode='w')
    fileHandler.setLevel(logging.DEBUG)
    logger.addHandler(fileHandler)
    formatter = logging.Formatter('%(asctime)s pid-%(process)d %(name)s %(levelname)s: %(message)s')
    fileHandler.setFormatter(formatter)
    return logger
    