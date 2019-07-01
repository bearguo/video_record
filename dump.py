import multiprocessing
import os
import shutil
import threading
import time
from ctypes import cdll, c_int, c_char_p
from datetime import datetime, timedelta

import dateutil

import dbutil
import epg
import global_var as globv
import logutil
import m3u8maker
from global_var import try_and_log

update_flag = True
START_TIME = datetime.now() - timedelta(days=1)
libtest = cdll.LoadLibrary(globv.cur_path + 'libUDP2HLS.so.1.0.0')
libtest.dump.argtype = [c_int, c_char_p, c_int]
dump = libtest.dump


def updateEpg(live_channel):
    for channel_id in live_channel:
        epg.update(channel_id)
        globv.update_logger.debug('update epg :' + channel_id)

def updateM3u8File(live_channel):
    for channel_id in live_channel:
        globv.update_logger.debug('update m3u8 file %s' % channel_id)
        program_list = dbutil.get_available_program(channel_id, START_TIME)
        dbutil.delete_conflit_program(program_list)
        globv.update_logger.debug(
            channel_id + '  available list' + str(program_list))
        for program in program_list:
            st = datetime.strptime(program['st'], '%Y-%m-%d %H:%M:%S')
            et = datetime.strptime(program['et'], '%Y-%m-%d %H:%M:%S')
            event_id = program['event_id']
            create_m3u8_file(channel_id, st, et, event_id)

def deleteExpireProgram(days, live_channel):
    now = datetime.now()
    for channel_id in live_channel:
        dbutil.delete_expire_program(channel_id, expire=days)
        channel_path = os.path.join(globv.html_path, channel_id)
        for dir_path, dir_names, file_names in os.walk(channel_path):
            for dir_name in dir_names:
                t = dateutil.folder2time(dir_name)
                if t is not None:
                    if now - t > timedelta(days=days):
                        folder = os.path.join(channel_path, dir_name)
                        delete_folder(folder)
                        globv.update_logger.debug('delete ' + folder)


def update_schedule():
    globv.update_logger.debug('update!')
    live_channel = dbutil.get_started_channels()
    try:
        updateM3u8File(live_channel)
        updateEpg(live_channel)
        deleteExpireProgram(globv.EXPIRE, live_channel)
    except Exception as e:
        globv.update_logger.error(e)
    finally:
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
        filename = m3u8maker.create_m3u8_file(
            channel_id, st, ts_path, file_list)
        globv.update_logger.debug('create m3u8 file: ' + filename)
        if filename is not None:
            url = 'http://%s/%s/%s/%s' % (globv.IP,
                                          channel_id, folder, filename)
            dbutil.update_url(channel_id, url, event_id)


@try_and_log
def start_channel(channel_id):
    process = multiprocessing.Process(
        name=channel_id, target=Dump2, args=(channel_id,))
    process.daemon = True
    process.start()
    globv.update_logger.info('start %s process done' % channel_id)
    epg.update(channel_id)


def restore_channels():
    for channel_id in dbutil.get_started_channels():
        globv.update_logger.info(
            'Restore recording channel %s start' % channel_id)
        start_channel(channel_id)
        time.sleep(.2)


@try_and_log
def get_udp_port(url):
    url = str(url)
    if 'udp' in url:
        return int(url[url.rfind(':') + 1:])
    else:
        return None

'''Not used
def get_udp_ip(url):
    url = str(url)
    if 'udp' in url:
        return url[url.rfind('/') + 1:url.rfind(':')]
    else:
        return None
'''

def Dump2(channel_id):
    port = dbutil.get_udp_port(channel_id)
    if port is None:
        globv.update_logger.error(
            'channel %s \'s address don\'t have a port number!' % channel_id)
        return

    channel_path = os.path.join(globv.html_path, channel_id)
    if not os.path.exists(channel_path):
        globv.update_logger.info('create path: %s' % channel_path)
        os.makedirs(channel_path)
    logger = logutil.getLogger(os.path.join(
        channel_path, channel_id + '.log'), name=channel_id)
    logger.debug('%s start record with dump()' % channel_id)
    try:
        while True:
            dump(port, channel_path.encode(), 60)
            time.sleep(60 * 5)
    except Exception as e:
        logger.exception(e)
        t = threading.Timer(5, Dump2, args=(channel_id,))
        t.start()

@try_and_log
def kill(channel_id): 
    dbutil.set_start(channel_id, False)
    globv.update_logger.info('kill ' + channel_id + ' done.')

def delete_folder(folder):
    shutil.rmtree(folder)

if __name__ == '__main__':
    pass