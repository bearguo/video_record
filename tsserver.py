from flask import Flask, request, make_response
import dump
from dump import start_channel, kill, error_map
from functools import wraps
import os
import threading
import configparser
import ldbutil
from global_var import *

cf = configparser.ConfigParser()
cf.read(cur_path + 'replay.conf')
PORT = cf.getint('server', 'port')
app = Flask(__name__, static_folder='.', static_url_path='')
update_flag = True


def allow_cross_domain(fun):
    @wraps(fun)
    def wrapper_fun(*args, **kwargs):
        rst = make_response(fun(*args, **kwargs))
        rst.headers['Access-Control-Allow-Origin'] = '*'
        rst.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
        allow_headers = "Referer,Accept,Origin,User-Agent"
        rst.headers['Access-Control-Allow-Headers'] = allow_headers
        return rst

    return wrapper_fun


@app.route('/echo/<thing>')
def echo(thing):
    return 'hello %s' % thing


@app.route('/status/<id>')
@allow_cross_domain
def status(id):
    # res = ldbutil.get_err(id)
    res = ""
    if id in error_map:
        res = error_map[id]
    if res == None:
        res = ""
    return res


@app.route('/replay-client/am')
def am():
    op, c = request.values.get('op'), request.values.get('c')
    if op == 'start':
        start_channel(c)
    elif op == 'kill':
        kill(c)
    return ''


def update():
    t = threading.Timer(10, update_schedule)
    t.start()


def update_schedule():
    print('dump update!')
    if update_flag:
        t = threading.Timer(10, update_schedule)
        t.start()


if __name__ == '__main__':
    # os.chdir('/home/share/replay/')
    dump.update()
    ldbutil.clear()
    app.run(host='0.0.0.0', port=9999, debug=False)
    dump.update_flag = False
    print('called here')
