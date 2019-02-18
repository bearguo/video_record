import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from time import sleep

LEVEL = logging.DEBUG


def getLogger(filename, name=None, level=LEVEL):
    logging.basicConfig(level=level,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(name)

    # make sure that the file exists
    if not os.path.exists(filename):
        file_path, file_name = os.path.split(filename)
        os.makedirs(file_path,exist_ok=True)
        # os.mknod(filename,mode=0o777)
        with open(filename, 'a+') as fp:
            pass
    # interval: how many numbers of 'when' will keep the log file
    # backupCount: how many old log files will keep.
    # log_file_handler = TimedRotatingFileHandler(filename=filename, when="D", interval=30, backupCount=3)
    log_file_handler = RotatingFileHandler(filename=filename, maxBytes=50*1024*1024, backupCount=3)

    log_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(filename)s(line %(lineno)d) - %(levelname)s - %(message)s'))
    logger.setLevel(level)
    logger.addHandler(log_file_handler)
    logger.debug('Log file created. File name: %s Logger name: %s'%(filename, name))
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
