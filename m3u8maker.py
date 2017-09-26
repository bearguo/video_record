# -*- coding: utf-8 -*-
import os
from string import ascii_letters
import dateutil
import random


def create_random_name():
    random_code_list = list(ascii_letters) + list('0123456789')
    slice = random.sample(random_code_list, 4)  # select 4 elements from code_list.
    random_string = ''.join(slice)  # list to string
    return random_string


def create_m3u8_file(event_id, ts_path, file_list):
    filename = create_random_name() + str(event_id) + '.m3u8'
    max = -1
    for file in file_list:
        inf = int(float(dateutil.get_inf_from_filename(file))) + 1
        if inf > max:
            max = inf

    with open(os.path.join(ts_path, filename), 'w') as fout:
        fout.write('#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-ALLOW-CACHE:NO\n')
        fout.write('#EXT-X-TARGETDURATION:%d\n' % max)

        for file in file_list:
            fout.write('#EXTINF:' + str(dateutil.get_inf_from_filename(file)) + '\n')
            fout.write(file + '\n')

        fout.write('#EXT-X-ENDLIST')
    return filename


if __name__ == '__main__':
    # create_m3u8_file('/var/www/html/CCTV2/test.m3u8',None)
    print(create_random_name())
