from datetime import datetime, timedelta
import time
import m3u8parser
import m3u8maker
from m3u8parser import TSFile
import threading
import os
import configparser
import multiprocessing
from multiprocessing import Manager
import dateutil
import dbutil
import epg
import logutil
import shutil
import ldbutil
from ctypes import *
from global_var import *

cf = configparser.ConfigParser()
cf.read(cur_path + 'replay.conf')
html_path = cf.get('dump', 'html_path')
channel_map = {}
error_map = {}
manager = Manager()
error_map = manager.dict()
ldbutil.init()
update_flag = True
START_TIME = datetime.now() - timedelta(hours=1)
UPDATE_FREQUENCE = cf.getint('dump', 'update_frequence')
IP = cf.get('server', 'ip')
EXPIRE = cf.getint('dump', 'expire') + 1
update_logger = logutil.getLogger(html_path + 'dump.log', name='dump')
libtest = cdll.LoadLibrary(cur_path + 'libUDP2HLS.so.1.0.0')
libtest.dump.argtype = [c_int, c_char_p, c_int]
dump = libtest.dump


def update():
    t = threading.Timer(UPDATE_FREQUENCE * 60, update_schedule)
    t.start()


def update_schedule():
    update_logger.debug('update!')
    # print(channel_map)
    update_logger.debug('channel_map --' + str(channel_map))
    try:
        if update_flag:
            # create m3u8 file
            for channel_id in channel_map:
                if channel_map[channel_id].is_alive():
                    list = dbutil.get_available_program(channel_id, START_TIME)
                    update_logger.debug(channel_id + '  available list' + str(list))
                    for program in list:
                        st = datetime.strptime(program['st'], '%Y-%m-%d %H:%M:%S')
                        et = datetime.strptime(program['et'], '%Y-%m-%d %H:%M:%S')
                        event_id = program['event_id']
                        create_m3u8_file(channel_id, st, et, event_id)
                        update_logger.debug('create m3u8 file ' + str(id))
                    pass
                else:
                    update_logger.debug('restart channel:' + channel_id)
                    # del channel_map[channel_id]
                    kill(channel_id)
                    start_channel(channel_id)

            # update epg
            for channel_id in channel_map:
                if channel_map[channel_id].is_alive():
                    epg.update(channel_id)
                    update_logger.debug('update epg :' + channel_id)

            # delete
            now = datetime.now()
            for channel_id in channel_map:
                dbutil.delete_expire_program(channel_id, expire=EXPIRE)
                channel_path = html_path + channel_id + '/'
                for dir_path, dir_names, file_names in os.walk(channel_path):
                    # print(dir_names)
                    for dir_name in dir_names:
                        # print(dir_name)
                        t = dateutil.folder2time(dir_name)
                        if t != None:
                            print(t)
                            if now - t > timedelta(days=EXPIRE):
                                delete_folder(channel_path + dir_name + '/')
                                update_logger.debug('delete ' + channel_path + dir_name + '/')
    finally:
        if update_flag:
            t = threading.Timer(UPDATE_FREQUENCE * 60, update_schedule)
            t.start()


def create_m3u8_file(channel_id, st, et, event_id):
    channel_path = html_path + channel_id + '/'
    file_list = []
    folder = dateutil.get_folder_name(st)
    ts_path = channel_path + folder + '/'

    for dir_path, dir_names, file_names in os.walk(ts_path):
        for file in file_names:
            t = dateutil.filename2time(folder, file)
            if t == None:
                continue
            if st < t < et:
                file_list.append('../' + folder + '/' + file)

    if st.day != et.day:
        folder = dateutil.get_folder_name(et)
        ts_path = channel_path + folder + '/'
        for dir_path, dir_names, file_names in os.walk(ts_path):
            for file in file_names:
                t = dateutil.filename2time(folder, file)
                if t == None:
                    continue
                if st < t < et:
                    file_list.append('../' + folder + '/' + file)
    file_list.sort()

    if len(file_list) != 0:
        filename = m3u8maker.create_m3u8_file(event_id, ts_path, file_list)
        update_logger.debug('create file ' + filename)
        if filename != None:
            url = 'http://' + IP + '/' + channel_id + '/' + folder + '/' + filename
            dbutil.update_url(channel_id, url, event_id)


def start_channel(channel_id):
    global channel_map
    if dbutil.is_start(channel_id):
        return
    if channel_id in channel_map:
        if channel_map[channel_id].is_alive():
            return
    dbutil.set_start(channel_id, True)
    error_map[channel_id] = "success"
    ldbutil.update_err(channel_id, 'success')
    process = multiprocessing.Process(name=channel_id, target=Dump2, args=(channel_id,))
    process.start()
    channel_map[channel_id] = process
    epg.update(channel_id)
    update_logger.debug('start ' + channel_id)
    # channel_map[channel_id] = os.getpid()


def rtmp2m3u8(url):
    url = str(url)
    if url.find('http') != -1:
        return url
    else:
        url = url.replace('rtmp', 'http')
        url = url + '.m3u8'
        return url


def get_prefix(url):
    url = str(url)
    url = url[0:url.rfind('/') + 1]
    return url


def get_udp_port(url):
    url = str(url)
    # if (url.__contains__("udp")):
    if ("udp" in url):
        return int(url[url.rfind(':') + 1:])
    else:
        return -1


def get_udp_ip(url):
    url = str(url)

    if url.__contains__("udp"):
        return url[url.rfind('/') + 1:url.rfind(':')]
    else:
        return None


def Dump2(channel_id):
    global error_map
    # url = str(dbutil.get_live_url(channel_id))  # udp://1.8.23.93:10000
    port = dbutil.get_udp_port(channel_id)
    # ip = get_udp_ip(url)
    if port is None:
        error_map[channel_id] = "wrong stream"
        # ldbutil.update_err(channel_id, 'wrong stream')
        dbutil.set_start(channel_id, False)
        return
    # if not IP.__eq__(ip):
    #     error_map[channel_id] = "wrong url"
    #     return

    channel_path = os.path.join(html_path, channel_id)

    if not os.path.exists(channel_path + '/'):
        os.makedirs(channel_path + '/')

    logger = logutil.getLogger(os.path.join(channel_path, channel_id + '.log'), name=channel_id)

    try:
        while True:
            error_map[channel_id] = "success"
            logger.debug(channel_id + ' start')
            # ldbutil.update_err(channel_id, 'success')

            res = dump(port, channel_path.encode(), 60)
            if res != 0:
                error_map[channel_id] = "no stream"
                logger.debug(channel_id + ' stopped!')
                # ldbutil.update_err(channel_id, 'no stream')

            time.sleep(60 * 5)
    finally:
        dbutil.set_start(channel_id, False)


def kill(channel_id):
    global channel_map
    try:
        if channel_id in channel_map:
            process = channel_map[channel_id]
            process.terminate()
            update_logger.info('kill ' + channel_id)
        else:
            raise ValueError('channel_id(%s) to be killed is not exist!'%channel_id)
    except Exception as e:
        update_logger.exception(e)
    finally:
        error_map[channel_id] = 'killed'
        dbutil.set_start(channel_id, False)
        if channel_id in channel_map:
            channel_map.pop(channel_id)
        update_logger.info('kill ' + channel_id + ' done.')


def delete_folder(folder):
    shutil.rmtree(folder)
    print('rm success')


def worker(lock):
    time.sleep(60)


if __name__ == '__main__':
    pass
    # try:
    #     Dump()
    # finally:
    #     g_flag = False

    # muti process test
    # lock = multiprocessing.Lock()
    # # for i in range(5):
    # process = multiprocessing.Process(target=start_channel, args=('CCTV1',))
    # process.start()
    # channel_map['CCTV1'] = process
    #
    # process2 = multiprocessing.Process(target=start_channel, args=('CCTV2',))
    # process2.start()
    # channel_map['CCTV2'] = process2
    # process2.terminate()
    #
    # print(channel_map)
    #
    # time.sleep(5)
    #
    # print(channel_map)


    # print(html_path)

    # st = datetime.strptime('2016-11-23 15:20:00', '%Y-%m-%d %H:%M:%S')
    # et = datetime.strptime('2016-11-23 15:30:00', '%Y-%m-%d %H:%M:%S')
    #
    # create_m3u8_file('CCTV2',st,et)

    # delete_folder('test/')

    # delete
    # channel_path = html_path + 'CCTV3' + '/'
    # now = datetime.now()
    # for dir_path, dir_names, file_names in os.walk(channel_path):
    #     # print(dir_names)
    #     for dir_name in dir_names:
    #         # print(dir_name)
    #         t = dateutil.folder2time(dir_name)
    #         if t != None:
    #             print(t)
    #             if now - t > timedelta(days=EXPIRE):
    #                 print('delete ' + dir_name)
    print(get_udp_port('udp://1.8.23.93:10000'))
    print(get_udp_ip('udp://1.8.23.93:10000'))
