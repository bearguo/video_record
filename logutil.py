import logging
from logging.handlers import TimedRotatingFileHandler
from time import sleep

LEVEL = logging.DEBUG


def getLogger(filename, name=None):
    logging.basicConfig(level=LEVEL,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(name)
    # interval: how many numbers of 'when' will keep the log file
    # backupCount: how many old log files will keep.
    log_file_handler = TimedRotatingFileHandler(filename=filename, when="D", interval=30, backupCount=3)
    log_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.setLevel(LEVEL)
    logger.addHandler(log_file_handler)
    logger.debug('Log file created.')
    return logger


if __name__ == '__main__':
    logger1 = getLogger('test1.log', 'logger1')
    logger2 = getLogger('test2.log', 'logger2')
    # logger3 = getLogger('test3.log','logger3')
    for i in range(10):
        sleep(.5)
        logger1.debug('test1')
        logger2.debug('test2')
    # logger3.debug('test3')

    pass
