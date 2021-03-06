import logging
import signal

from burlesque import Burlesque
from momoko import Pool
from tornado import autoreload
from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop
from tornado.options import define, options, parse_command_line

from core.slave_holder import SlaveHolder


if __name__ == '__main__':
    define('db', type=str, help='DB connection DSN', default="dbname=boterator user=boterator host=localhost port=5432")
    define('burlesque', default='http://127.0.0.1:4401', type=str, help='Burlesque address')
    define('debug', type=bool, default=False)

    parse_command_line()

    AsyncHTTPClient.configure(None, max_clients=1024)

    ioloop = IOLoop.instance()

    db = Pool(dsn=options.db, size=1, max_size=10, auto_shrink=True, ioloop=IOLoop.current())
    ioloop.run_sync(db.connect)

    if options.debug:
        autoreload.start()

    sh = SlaveHolder(db, Burlesque(options.burlesque))
    try:
        ioloop.run_sync(sh.start)
    except Exception as e:
        if not isinstance(e, KeyboardInterrupt):
            logging.exception('Got exception')
        sh.stop()

    signal.signal(signal.SIGTERM, sh.stop)
    signal.signal(signal.SIGINT, sh.stop)
