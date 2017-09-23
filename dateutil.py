from _datetime import datetime


def get_folder_name(t):
    return str(t.year) + '{:0>2}'.format(str(t.month)) + '{:0>2}'.format(str(t.day))


def filename2time(folder, filename):
    if filename.find('.ts') == -1:
        return None

    t = datetime(year=int(folder[0:4]),month=int(folder[4:6]),day=int(folder[6:8]), hour=int(filename[0:2]),minute=int(filename[2:4]),second=int(filename[4:6]))

    return t


def folder2time(folder):
    if len(folder) != 8:
        return None

    t = datetime(year=int(folder[0:4]),month=int(folder[4:6]),day=int(folder[6:8]), hour=0,minute=0)

    return t


def get_inf_from_filename(filename):
    return filename[-9:-3]



if __name__ == '__main__':
    print(filename2time('20161123','1523-73.558.ts'))
    print(get_inf_from_filename('1523-73.558.ts'))

    print(folder2time('20161123'))