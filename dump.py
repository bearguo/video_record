import os
from datetime import datetime, timedelta
import time

import logutil
import m3u8maker
import threading
import multiprocessing
from multiprocessing import Manager
import dateutil
import dbutil
import epg
import shutil
import ldbutil
from ctypes import *
import global_var as globv
from global_var import try_and_log

channel_map = {}
manager = Manager()
error_map = manager.dict()
ldbutil.init()
update_flag = True
START_TIME = datetime.now() - timedelta(days=1)
libtest = cdll.LoadLibrary(globv.cur_path + 'libUDP2HLS.so.1.0.0')
libtest.dump.argtype = [c_int, c_char_p, c_int]
dump = libtest.dump


def update():
    t = threading.Timer(globv.UPDATE_FREQUENCY * 60, update_schedule)
    t.setDaemon(True)
    t.start()


def updateEpg():
    for channel_id in channel_map:
        if channel_map[channel_id].is_alive():
            epg.update(channel_id)
            globv.update_logger.debug('update epg :' + channel_id)


def updateM3u8File():
    for channel_id in channel_map:
        if channel_map[channel_id].is_alive():
            globv.update_logger.debug('update m3u8 file %s'%channel_id)
            program_list = dbutil.get_available_program(channel_id, START_TIME)
            dbutil.delete_conflit_program(program_list)
            globv.update_logger.debug(channel_id + '  available list' + str(program_list))
            for program in program_list:
                st = datetime.strptime(program['st'], '%Y-%m-%d %H:%M:%S')
                et = datetime.strptime(program['et'], '%Y-%m-%d %H:%M:%S')
                event_id = program['event_id']
                create_m3u8_file(channel_id, st, et, event_id)
                globv.update_logger.debug('create m3u8 file ' + str(id))
        else:
            globv.update_logger.debug('restart channel:' + channel_id)
            # del channel_map[channel_id]
            kill(channel_id)
            start_channel(channel_id)


def deleteExpireProgram(days):
    now = datetime.now()
    for channel_id in channel_map:
        dbutil.delete_expire_program(channel_id, expire=days)
        channel_path = os.path.join(globv.html_path, channel_id)
        for dir_path, dir_names, file_names in os.walk(channel_path):
            # print(dir_names)
            for dir_name in dir_names:
                # print(dir_name)
                t = dateutil.folder2time(dir_name)
                if t is not None:
                    print(t)
                    if now - t > timedelta(days=days):
                        folder = os.path.join(channel_path, dir_name)
                        delete_folder(folder)
                        globv.update_logger.debug('delete ' + folder)


def update_schedule():
    globv.update_logger.debug('update!')
    # print(channel_map)
    globv.update_logger.debug('channel_map --' + str(channel_map))
    try:
        if update_flag:
            # create m3u8 file
            updateM3u8File()
            updateEpg()
            # delete
            deleteExpireProgram(globv.EXPIRE)
    finally:
        if update_flag:
            t = threading.Timer(globv.UPDATE_FREQUENCY * 60, update_schedule)
            t.start()


def genFileList(folder, ts_path, st, et):
    file_list = []
    for dir_path, dir_names, file_names in os.walk(ts_path):
        for file in file_names:
            t = dateutil.filename2time(folder, file)
            if t is None:
                continue
            if st < t < et:
                file_list.append(os.path.join(os.path.pardir, folder, file))
    return file_list


def create_m3u8_file(channel_id, st, et, event_id):
    channel_path = os.path.join(globv.html_path, channel_id)
    folder = dateutil.get_folder_name(st)
    ts_path = os.path.join(channel_path, folder)

    file_list = genFileList(folder, ts_path, st, et)

    if st.day != et.day:
        folder = dateutil.get_folder_name(et)
        ts_path = os.path.join(channel_path, folder)
        file_list += genFileList(folder, ts_path, st, et)

    file_list.sort()

    if len(file_list) != 0:
        filename = m3u8maker.create_m3u8_file(event_id, ts_path, file_list)
        globv.update_logger.debug('create m3u8 file: ' + filename)
        if filename is not None:
            url = 'http://%s/%s/%s/%s' %(globv.IP, channel_id, folder, filename)
            dbutil.update_url(channel_id, url, event_id)


@try_and_log
def start_channel(channel_id):
    global channel_map
    # if dbutil.is_start(channel_id):
    #     return
    if channel_id in channel_map:
        if channel_map[channel_id].is_alive():
            return
    dbutil.set_start(channel_id, True)
    error_map[channel_id] = "success"
    ldbutil.update_err(channel_id, 'success')
    process = multiprocessing.Process(name=channel_id, target=Dump2, args=(channel_id,))
    process.daemon = True
    process.start()
    globv.update_logger.info('start %s process done' % channel_id)
    channel_map[channel_id] = process
    epg.update(channel_id)


def restore_channels():
    for channel_id in dbutil.get_started_channels():
        globv.update_logger.info('Restore recording channel %s start'%channel_id)
        start_channel(channel_id)
        time.sleep(.2)


@try_and_log
def get_udp_port(url):
    url = str(url)
    if 'udp' in url:
        return int(url[url.rfind(':') + 1:])
    else:
        return None


def get_udp_ip(url):
    url = str(url)
    if 'udp' in url:
        return url[url.rfind('/') + 1:url.rfind(':')]
    else:
        return None


def Dump2(channel_id):
    global error_map
    globv.update_logger.info('start record %s' % channel_id)
    port = dbutil.get_udp_port(channel_id)
    if port is None:
        error_map[channel_id] = 'wrong stream'
        globv.update_logger.error('channel %s \'s address don\'t have a port number!' % channel_id)
        dbutil.set_start(channel_id, False)
        return

    channel_path = os.path.join(globv.html_path, channel_id)
    if not os.path.exists(channel_path):
        globv.update_logger.info('create path: %s' % channel_path)
        os.makedirs(channel_path)
    logger = logutil.getLogger(os.path.join(channel_path, channel_id + '.log'), name=channel_id)

    try:
        while True:
            error_map[channel_id] = "success"
            logger.debug('%s start record with dump()' % channel_id)
            res = dump(port, channel_path.encode(), 60)
            if res != 0:
                error_map[channel_id] = 'no stream'
                ldbutil.update_err(channel_id,'no stream')
                logger.debug(channel_id + ' stopped by dump()!')
                globv.update_logger.error('channel %s stopped by dump()!'%channel_id)
            time.sleep(60 * 5)
    except Exception as e:
        logger.exception(e)
    finally:
        dbutil.set_start(channel_id, False)


@try_and_log
def kill(channel_id):
    global channel_map
    try:
        if channel_id in channel_map:
            process = channel_map[channel_id]
            process.terminate()
            globv.update_logger.info('kill ' + channel_id)
        else:
            raise ValueError('channel_id(%s) to be killed is not exist!' % channel_id)
    except Exception as e:
        globv.update_logger.exception(e)
    finally:
        error_map[channel_id] = 'killed'
        dbutil.set_start(channel_id, False)
        if channel_id in channel_map:
            channel_map.pop(channel_id)
        globv.update_logger.info('kill ' + channel_id + ' done.')


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
