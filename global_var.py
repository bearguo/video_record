import configparser
import os
import logutil

cur_path = os.path.dirname(os.path.realpath(__file__)) + '/'
cf = configparser.ConfigParser()
cf.read(cur_path + 'replay.conf')
html_path = cf.get('dump', 'html_path')
update_logger = logutil.getLogger(html_path + 'dump.log', name='dump')

cf = configparser.ConfigParser()
cf.read(cur_path + 'replay.conf')
html_path = cf.get('dump', 'html_path')
update_logger = logutil.getLogger(html_path + 'dump.log', name='dump')

def try_and_log(function):
    def wraps(*args, **kwargs):
        val=None
        try:
            val = function(*args, **kwargs)
        except Exception as e:
            update_logger.exception(e)
        return val
    return wraps


@try_and_log
def divide(a,b):
    return a/b

if __name__ == '__main__':
    print(cur_path)
    divide(1,0)
    print('done')