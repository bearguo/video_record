import configparser
from datetime import datetime,timedelta
import urllib.request as ur
import xml.etree.ElementTree as et
import dbutil

from global_var import *

cf = configparser.ConfigParser()
cf.read(cur_path+'replay.conf')

EPG_URL = cf.get('dump','epg_url')


@try_and_log
def update(channel_id):
    # print(EPG_URL + channel_id)
    try:
        tree = et.parse(ur.urlopen(EPG_URL + channel_id))
    except:
        return

    if tree == None:
        return

    dbutil.delete_program(channel_id)

    root = tree.getroot()
    now = datetime.now()
    for schedule in root.iter('schedule'):
        for event in schedule.findall('event'):
            event_id = event.get('id')
            date = datetime.strptime(schedule.get('date'), '%Y-%m-%d').date()
            start_time = event.find('start_time').text
            start_time = datetime.strptime(start_time, '%H:%M').time()

            end_time = event.find('end_time').text
            end_time = datetime.strptime(end_time, '%H:%M').time()
            title = event.find('title').text
            title = title.replace("'", "\\'").replace("\\", "\\'").replace("·", "\\'")


            if start_time > end_time:
                start_dt = datetime.combine(date, start_time)
                end_dt = datetime.combine(date + timedelta(days=1), end_time)
            else:
                start_dt = datetime.combine(date, start_time)
                end_dt = datetime.combine(date , end_time)

            # print(title + ' ' + str(start_dt) + ' ' + str(end_dt))

            if end_dt > now :
                dbutil.insert_program(event_id,channel_id,start_dt,end_dt,title)



if __name__ == '__main__':
    update('CCTV2')

    # print(EPG_URL)
