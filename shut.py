import ldbutil
import dbutil
import os


def kill(channel_id):
    dbutil.set_start(channel_id, False)
    pass


def kill_all_channel():
    list = ldbutil.get_channels()

    for channel in list:
        kill(channel)

    ldbutil.clear()


if __name__ == '__main__':
    os.chdir('/home/share/replay/')
    kill_all_channel()
