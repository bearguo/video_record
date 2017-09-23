import logging

LEVEL = logging.DEBUG

def getLogger(filename,name=None):

    if name == None:
        logger = logging.getLogger()
    else:
        logger = logging.getLogger(name)

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh = logging.FileHandler(filename)

    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    logger.debug('Log file created.')

    return logger

if __name__ == '__main__':

    logger1 = getLogger('test1.log','logger1')
    logger2 = getLogger('test2.log','logger2')
    logger3 = getLogger('test3.log','logger3')

    logger1.debug('test1')
    logger2.debug('test2')
    logger3.debug('test3')

    pass