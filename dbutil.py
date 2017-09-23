import pymysql.cursors
import configparser
import os
from datetime import datetime,timedelta
from global_var import *

cf = configparser.ConfigParser()
cf.read(cur_path+'replay.conf')

HOST = cf.get('db','host')
PORT = cf.getint('db','port')
USER = cf.get('db','user')
PASSWORD = cf.get('db','password')



def connect():
    conn = pymysql.connect(host=HOST,
                           port=PORT,
                           user=USER,
                           password=PASSWORD,
                           db='tsrtmp',
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)

    return conn


def get_channel_info(channel_id):
    conn = connect()
    with conn.cursor() as cursor:
        sql = "SELECT * FROM channel WHERE channel_id = '%s'" % channel_id
        cursor.execute(sql)
        result = cursor.fetchone()
        # print(result)

    conn.close()
    return result


def get_live_url(channel_id):
    return get_channel_info(channel_id)['rtmp_url']



def get_udp_port(channel_id):
    port = str(get_channel_info(channel_id)['client_ip'])

    if port.__contains__(':'):
        res = port[port.rfind(':')+1:]
        return int(res)
    else:
        return None


def set_start(channel_id,active):
    conn = connect()
    status = ''
    if active:
        status = '1'
    else:
        status = '0'

    with conn.cursor() as cursor:
        sql = "UPDATE channel SET start = %s WHERE channel_id = '%s'" % (status,channel_id)
        cursor.execute(sql)
        conn.commit()

    conn.close()


def is_start(channel_id):
    active = get_channel_info(channel_id)['start']
    if active == 1:
        return True
    else:
        return False

def get_available_program(channel_id,START_TIME):
    conn = connect()
    ret = []
    with conn.cursor() as cursor:
        sql = "SELECT DATE_FORMAT(start_time,'%%Y-%%m-%%d %%H:%%i:%%S') AS st, \
                         DATE_FORMAT(end_time,'%%Y-%%m-%%d %%H:%%i:%%S') AS et,title,event_id \
                         FROM program WHERE channel_id = '%s' AND finished = 0 \
                         ORDER BY end_time" % channel_id
        cursor.execute(sql)
        result = cursor.fetchall()

    now = datetime.now()

    for program in result:
        et = datetime.strptime(program['et'], '%Y-%m-%d %H:%M:%S')
        if START_TIME < et < now:
            ret.append(program)

    return ret


def delete_program(channel_id):
    conn = connect()

    with conn.cursor() as cursor:
        sql = "DELETE FROM program WHERE channel_id='%s' and finished=0" % channel_id
        cursor.execute(sql)
        conn.commit()

    conn.close()


def insert_program(event_id, channel_id, st, et, title):
    conn = connect()

    with conn.cursor() as cursor:
        sql = "INSERT IGNORE INTO program(event_id,channel_id,start_time,end_time,title) \
                                            VALUES ('%s','%s','%s','%s','%s')" % \
                                                (event_id, channel_id, st, et, title)
        cursor.execute(sql)
        conn.commit()

    conn.close()


def update_url(channel_id,url,event_id):
    conn = connect()

    with conn.cursor() as cursor:
        sql = "UPDATE program SET finished = 1, url = '%s' \
                        WHERE event_id = '%s'" % (url, event_id)
        cursor.execute(sql)
        conn.commit()

    # print('update url ' + url)
    conn.close()


def delete_expire_program(channel_id,expire=8):
    conn = connect()

    with conn.cursor() as cursor:
        sql = "DELETE FROM program WHERE channel_id = '%s' AND end_time < DATE_SUB(NOW(), INTERVAL %d DAY)" % (channel_id,expire)
        cursor.execute(sql)
        conn.commit()

    conn.close()


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

    print(get_udp_port('CCTV2'))


