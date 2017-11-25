import configparser
import logging
import os
import logutil
import sys


if getattr(sys, 'frozen', False):
    cur_path = os.path.dirname(sys.executable) + '/'
elif __file__:
    cur_path = os.path.dirname(os.path.realpath(__file__)) + '/'
#cur_path = os.path.dirname(os.path.realpath(__file__)) + '/'
cf = configparser.ConfigParser()
global UPDATE_FREQUENCY, IP, EXPIRE, update_logger, html_path, PORT, EPG_URL


def initConfigFile():
    global UPDATE_FREQUENCY, IP, EXPIRE, update_logger, html_path, PORT, EPG_URL
    config_file_name = 'replay.conf'
    try:
        config_file = os.path.join(cur_path, config_file_name)
        if not os.path.exists(config_file):
            raise ValueError('%s is not exists in current folder!'%config_file_name)
        cf.read(config_file)
        html_path = cf.get('dump', 'html_path')
        UPDATE_FREQUENCY = cf.getint('dump', 'update_frequence')
        IP = cf.get('record_server', 'ip')
        EXPIRE = cf.getint('dump', 'expire') + 1
        update_logger = logutil.getLogger(os.path.join(html_path, 'dump.log'), name='dump')
        PORT = cf.getint('record_server', 'port')
        EPG_URL = cf.get('dump', 'epg_url')
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


# class GlobalVar():
#     def __init__(self):#初始化
#         global _global_dict
#         _global_dict = {}
#
#
#     def set_value(key,value):
#         """ 定义一个全局变量 """
#         _global_dict[key] = value
#
#
#     def get_value(key,defValue=None):
#         """ 获得一个全局变量,不存在则返回默认值 """
#         try:
#             return _global_dict[key]
#         except KeyError:
#             return defValue

if __name__ == '__main__':
    print(cur_path)
    divide(1,0)
    print('done')
