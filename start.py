from gunicorn.app.base import Application, Config
import gunicorn
from gunicorn import glogging
from tsserver import app
import multiprocessing
from gunicorn.workers import ggevent
from tsserver import init_app, after_app, app
import global_var as globv

class GUnicornFlaskApplication(Application):
    def __init__(self, app):
        self.usage, self.callable, self.prog, self.app = None, None, None, app

    def run(self, **options):
        self.cfg = Config()
        [self.cfg.set(key, value) for key, value in options.items()]
        return Application.run(self)

    load = lambda self:self.app

if __name__ == "__main__":
    init_app()
    gunicorn_app = GUnicornFlaskApplication(app)
    gunicorn_app.run(
        worker_class="gunicorn.workers.ggevent.GeventWorker",
        bind='0.0.0.0:%s'%globv.PORT,
        workers = multiprocessing.cpu_count() * 2 + 1,
        # 如果不使用supervisord之类的进程管理工具可以是进程成为守护进程，否则会出问题
        daemon = False,

        # 进程名称
        proc_name = 'tsserver',

        # 进程pid记录文件
        pidfile = 'tsserver.pid',

        loglevel = 'debug',
        accesslog = 'access.log',
        access_log_format = '%(h)s %(t)s %(U)s %(q)s',
        errorlog = 'error.log',
        # 每个进程的开启线程
        threads = multiprocessing.cpu_count() * 2,
        backlog = 2048
    )
    after_app()
