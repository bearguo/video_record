# -*- coding: utf-8 -*-
import dateutil
import random

def create_random_name():
    random_code_list = []
    for i in range(10):  # 0-9
        random_code_list.append(str(i))
    for i in range(65, 91):  # A-Z
        random_code_list.append(chr(i))
    for i in range(97, 123):  # a-z
        random_code_list.append(chr(i))
    # select 12 elements from code_list.
    slice = random.sample(random_code_list, 4)
    r_str = ''.join(slice)  # list to string
    return r_str

def create_m3u8_file(event_id,ts_path,file_list):
    filename = create_random_name() + str(event_id) +'.m3u8'

    max = -1

    for file in file_list:
        inf = int(float(dateutil.get_inf_from_filename(file))) +1
        if inf > max:
            max = inf

    fout = open(ts_path + filename,'w')
    fout.write('#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-ALLOW-CACHE:NO\n')
    fout.write('#EXT-X-TARGETDURATION:%d\n' % max)

    for file in file_list:
        fout.write('#EXTINF:' + str(dateutil.get_inf_from_filename(file)) + '\n')
        fout.write(file + '\n')


    fout.write('#EXT-X-ENDLIST')
    fout.close()

    return filename

if __name__ == '__main__':

    # create_m3u8_file('/var/www/html/CCTV2/test.m3u8',None)
    print(create_random_name())