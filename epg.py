import configparser
import urllib.request as ur
import xml.etree.ElementTree as et
from datetime import datetime, timedelta

import dbutil
import global_var as globv
from global_var import *


@try_and_log
def update(channel_id):
    global EPG_URL
    tree = et.parse(ur.urlopen(globv.EPG_URL + channel_id))
    if tree is None:
        raise ValueError('epg tree is not available')

    dbutil.delete_program(channel_id)

    root = tree.getroot()
    now = datetime.now()
    latest = dbutil.get_finished_latest_date(channel_id)
    base_time = latest if latest else now
    for schedule in root.iter('schedule'):
        for event in schedule.findall('event'):
            event_id = event.get('id')
            date = datetime.strptime(schedule.get('date'), '%Y-%m-%d').date()
            start_time = event.find('start_time').text
            start_time = datetime.strptime(start_time, '%H:%M').time()

            end_time = event.find('end_time').text
            end_time = datetime.strptime(end_time, '%H:%M').time()
            title = event.find('title').text

            if start_time > end_time:
                start_dt = datetime.combine(date, start_time)
                end_dt = datetime.combine(date + timedelta(days=1), end_time)
            else:
                start_dt = datetime.combine(date, start_time)
                end_dt = datetime.combine(date, end_time)

            if end_dt > base_time:
                dbutil.insert_program(event_id, channel_id, start_dt, end_dt, title)


if __name__ == '__main__':
    update('CCTV1')
    print('update epg done')
