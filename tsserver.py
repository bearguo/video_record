import configparser
import os
import threading
from functools import wraps
# from werkzeug.contrib.fixers import ProxyFix
from pathlib import Path

from flask import Flask, make_response, request

import dump
import global_var as globv
from dbutil import get_started_channels, initDBSettings
from dump import error_map, kill, restore_channels, start_channel
from global_var import try_and_log

app = Flask(__name__, static_folder='.', static_url_path='')
# app.wsgi_app = ProxyFix(app.wsgi_app)
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
    live_channel = get_started_channels()
    res = ""
    if id in live_channel:
        res = 'success'
    if res == None:
        res = ""
    return res


@app.route('/replay-client/am')
def am():
    op, c = request.values.get('op'), request.values.get('c')
    if op == 'start':
        start_channel(c)
    elif op == 'stop':
        kill(c)
    return ''


def init_app():
    globv.initConfigFile()
    initDBSettings()
    dump.update()
    globv.update_logger.info('='*20 + 'video record web server' + '='*20)
    globv.update_logger.info('='*20 + '  licensed by tongshi  ' + '='*20)


def after_app():
    dump.update_flag = False
    print('called here')


if __name__ == '__main__':
    globv.initConfigFile()
    initDBSettings()
    t = threading.Thread(target=app.run,kwargs={'host':'0.0.0.0','port':globv.PORT,'debug':False})
    t.setDaemon(True)
    t.start()
    globv.update_logger.info('='*20 + 'video record web server' + '='*20)
    globv.update_logger.info('='*20 + '  licensed by tongshi  ' + '='*20)
    restore_channels()
    dump.update_schedule()

#    ldbutil.clear()
#    dump.update_flag = False
