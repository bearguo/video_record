# -*- coding: utf-8 -*-
import os
import random
from string import ascii_letters

import dateutil


def create_m3u8_file(channel_id, st, ts_path, file_list):
    filename = str(channel_id) + str(st) + '.m3u8'
    max = -1
    for file in file_list:
        inf = int(float(dateutil.get_inf_from_filename(file))) + 1
        if inf > max:
            max = inf

    with open(os.path.join(ts_path, filename), 'w') as fout:
        fout.write('#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-ALLOW-CACHE:NO\n')
        fout.write('#EXT-X-TARGETDURATION:%d\n' % max)

        for file in file_list:
            fout.write(
                '#EXTINF:' + str(dateutil.get_inf_from_filename(file)) + '\n')
            fout.write(file + '\n')

        fout.write('#EXT-X-ENDLIST')
    return filename


if __name__ == '__main__':
    pass
