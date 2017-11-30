from flask import Flask, request, make_response
import dump
from dump import start_channel, kill, error_map
from functools import wraps
import os
import threading
import configparser
import ldbutil
import global_var as globv
from dbutil import initDBSettings
# from werkzeug.contrib.fixers import ProxyFix
from pathlib import Path
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
    elif op == 'stop':
        kill(c)
    return ''


def init_app():
    globv.initConfigFile()
    initDBSettings()
    dump.update()
    ldbutil.clear()
    globv.update_logger.info('='*20 + 'video record web server' + '='*20)
    globv.update_logger.info('='*20 + '  licensed by tongshi  ' + '='*20)


def after_app():
    dump.update_flag = False
    print('called here')

if __name__ == '__main__':
    globv.initConfigFile()
    initDBSettings()
    dump.update()
    ldbutil.clear()
    globv.update_logger.info('='*20 + 'video record web server' + '='*20)
    globv.update_logger.info('='*20 + '  licensed by tongshi  ' + '='*20)
    with (Path(globv.cur_path)/'tsserver.pid').open('w') as f:
        f.write(str(os.getpid()))
    app.run(host='0.0.0.0', port=globv.PORT, debug=False)
    dump.update_flag = False
    print('called here')
