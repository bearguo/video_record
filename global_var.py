import configparser
import os

cur_path = os.path.dirname(os.path.realpath(__file__)) + '/'
cf = configparser.ConfigParser()
cf.read(cur_path + 'replay.conf')
html_path = cf.get('dump', 'html_path')
update_logger = logutil.getLogger(html_path + 'dump.log', name='dump')

if __name__ == '__main__':
    print(cur_path)