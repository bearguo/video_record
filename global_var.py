import configparser
import logging
import os
import logutil

cur_path = os.path.dirname(os.path.realpath(__file__)) + '/'
cf = configparser.ConfigParser()
config_file_name = 'replay.conf'
try:
    config_file = os.path.join(cur_path, config_file_name)
    if not os.path.exists(config_file):
        raise ValueError('replay.conf is not exists in current folder!')
    cf.read(config_file)
    html_path = cf.get('dump', 'html_path')
    UPDATE_FREQUENCY = cf.getint('dump', 'update_frequence')
    IP = cf.get('server', 'ip')
    EXPIRE = cf.getint('dump', 'expire') + 1
    update_logger = logutil.getLogger(os.path.join(html_path, 'dump.log'), name='dump')
except Exception as e:
    logging.exception(e)
    exit(-1)

# Decorator: Log the exception information into html folder(dump.log)
def try_and_log(function):
    def wraps(*args, **kwargs):
        val = None
        try:
            val = function(*args, **kwargs)
        except Exception as e:
            update_logger.exception(e)
        return val

    return wraps


# Decorator: Log the exception information on the screen and EXIT program!
def fatal_error_exit(function):
    def wraps(*args, **kwargs):
        val = None
        try:
            val = function(*args, **kwargs)
        except Exception as e:
            logging.exception(e)
            exit(-1)
        return val

    return wraps


@try_and_log
def divide(a, b):
    return a / b


if __name__ == '__main__':
    print(cur_path)
    divide(1,0)
    print('done')
