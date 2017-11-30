import pymysql.cursors
import configparser
import os
from datetime import datetime, timedelta
import global_var as globv
from global_var import *

global HOST, PORT, USER, PASSWORD

def initDBSettings():
    global HOST, PORT, USER, PASSWORD
    try:
        HOST = cf.get('db', 'host')
        PORT = cf.getint('db', 'port')
        USER = cf.get('db', 'user')
        PASSWORD = cf.get('db', 'password')
    except Exception as e:
        logging.exception(e)
        exit(-1)


class Connect():
    def __init__(self):
        initDBSettings()

    def __enter__(self):
        global HOST, PORT, USER, PASSWORD
        self.connect = pymysql.connect(host=HOST,
                                       port=PORT,
                                       user=USER,
                                       password=PASSWORD,
                                       db='tsrtmp',
                                       charset='utf8mb4',
                                       cursorclass=pymysql.cursors.DictCursor)
        return self.connect

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connect.close()


# def connect():
#     conn = pymysql.connect(host=HOST,
#                            port=PORT,
#                            user=USER,
#                            password=PASSWORD,
#                            db='tsrtmp',
#                            charset='utf8mb4',
#                            cursorclass=pymysql.cursors.DictCursor)
#
#     return conn

'''
Get channel information by channel_id,return data fields.
return dictionary
    eg.:{'start': 0, 'sort': 0, 'rtmp_url': 'http://localhost/CCTV1.m3u8', 'client_ip': 'localhost:8080',
             'PID': None, 'channel_name': 'CCTV1', 'channel_id': 'CCTV1', 'id': 1, 'PGID': None, 'active': 0}
'''


def get_channel_info(channel_id):
    with Connect() as conn:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM channel WHERE channel_id = \'%s\'" % channel_id
            cursor.execute(sql)
            result = cursor.fetchone()
            # print(result)
    return result


def get_live_url(channel_id):
    return get_channel_info(channel_id)['rtmp_url']


@try_and_log
def get_udp_port(channel_id):
    address = str(get_channel_info(channel_id)['client_ip'])
    port = None
    try:
        if ':' in address:
            port_str = address[address.rfind(':') + 1:]
            port = int(port_str)  # make sure port_str is a number
    except Exception as e:
        globv.update_logger.exception(e)
    finally:
        return port

@try_and_log
def is_start(channel_id):
    active = get_channel_info(channel_id)['start']
    if active == 1:
        return True
    else:
        return False


def set_start(channel_id, active):
    with Connect() as conn:
        status = ''
        if active:
            status = '1'
        else:
            status = '0'

        with conn.cursor() as cursor:
            sql = "UPDATE channel SET start = %s WHERE channel_id = \'%s\'" % (status, channel_id)
            cursor.execute(sql)
            conn.commit()


def get_available_program(channel_id, START_TIME):
    with Connect() as conn:
        with conn.cursor() as cursor:
            sql = "SELECT DATE_FORMAT(start_time,'%%Y-%%m-%%d %%H:%%i:%%S') AS st, \
                             DATE_FORMAT(end_time,'%%Y-%%m-%%d %%H:%%i:%%S') AS et,title,event_id \
                             FROM program WHERE channel_id = \'%s\' AND finished = 0 \
                             ORDER BY end_time" % channel_id
            cursor.execute(sql)
            result = cursor.fetchall()
    now = datetime.now()
    # for program in result:
    #     et = datetime.strptime(program['et'], '%Y-%m-%d %H:%M:%S')
    #     if START_TIME < et < now:
    #         ret.append(program)
    ret = [program for program in result if START_TIME < datetime.strptime(program['et'], '%Y-%m-%d %H:%M:%S') <= now]
    globv.update_logger.debug('ret = %s'%str(ret))

    return ret


def delete_program(channel_id):
    with Connect() as conn:
        with conn.cursor() as cursor:
            sql = "DELETE FROM program WHERE channel_id=\'%s\' and finished=0" % channel_id
            cursor.execute(sql)
            conn.commit()


def insert_program(event_id, channel_id, st, et, title):
    title = pymysql.escape_string(title)
    with Connect() as conn:
        with conn.cursor() as cursor:
            sql = "INSERT IGNORE INTO program(event_id,channel_id,start_time,end_time,title) \
                                                VALUES ('%s','%s','%s','%s','%s')" % \
                  (event_id, channel_id, st, et, title)
            cursor.execute(sql)
            conn.commit()


def update_url(channel_id, url, event_id):
    with Connect() as conn:
        with conn.cursor() as cursor:
            sql = "UPDATE program SET finished = 1, url = \'%s\' \
                            WHERE event_id = \'%s\'" % (url, event_id)
            cursor.execute(sql)
            conn.commit()


def delete_expire_program(channel_id, expire=8):
    with Connect() as conn:
        with conn.cursor() as cursor:
            sql = "DELETE FROM program WHERE channel_id = \'%s\' AND end_time < DATE_SUB(NOW(), INTERVAL %d DAY)" % (
                channel_id, expire)
            cursor.execute(sql)
            conn.commit()


if __name__ == '__main__':
    # print(get_live_url('CCTV2'))
    #
    # print(is_start('CCTV2'))

    # set_start('CCTV1',True)
    #
    # print(is_start('CCTV1'))
    #
    # set_start('CCTV1',False)

    # print(get_available_program('CCTV2',datetime.now()-timedelta(days=2)))

    # print("DELETE FROM program WHERE channel_id = '%s' AND end_time < DATE_SUB(NOW(), INTERVAL %d DAY)" % ('CCTV1',8))
    get_channel_info('CCTV1')
    # print(get_udp_port('CCTV2'))
