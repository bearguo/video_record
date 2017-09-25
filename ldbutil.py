from tinydb import TinyDB, Query
import configparser

from global_var import *

cf = configparser.ConfigParser()
cf.read(cur_path + 'replay.conf')

file = cur_path + cf.get('local_db', 'file')


def init():
    db = TinyDB(file)
    # db.insert({'int': 1, 'char': 'a'})
    # print(db.all())
    db.purge()
    # print(db.all)
    pass


def update_err(channel_id, status):
    db = TinyDB(file)

    Channel = Query()
    res = db.search(Channel.id == channel_id)
    print(res)
    if len(res) == 0:
        db.insert({'id': channel_id, 'status': status})
    else:
        db.update({'status': status}, Channel.id == channel_id)

    # print(db.all())
    pass


def get_err(channel_id):
    # db = TinyDB(file)
    #
    # Channel = Query()
    # res = db.search(Channel.id == channel_id)
    #
    # if len(res) == 0:
    #     content = None
    # else:
    #     content = res[0]['status']

    return 'success'


def get_channels():
    db = TinyDB(file)
    ret = []
    all = db.all()

    for i in all:
        ret.append(i['id'])

    return ret


def clear():
    db = TinyDB(file)
    db.purge()


if __name__ == "__main__":
    init()
    update_err("CCTV1", "success")

    update_err("CCTV1", "no stream")

    print(get_err("CCTV1"))
    pass
