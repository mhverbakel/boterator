import signal

from burlesque import Burlesque
from momoko import Pool
from tornado.ioloop import IOLoop
from tornado.locale import load_gettext_translations
from tornado.options import define, options, parse_command_line, print_help

from core import Boterator


if __name__ == '__main__':
    define('token', type=str, help='TelegramBot\'s token')
    define('db', type=str, help='DB connection DSN', default="dbname=boterator user=boterator host=localhost port=5432")
    define('burlesque', default='http://127.0.0.1:4401', type=str, help='Burlesque address')

    parse_command_line()

    if not options.token:
        print_help()
        exit(1)

    ioloop = IOLoop.instance()

    db = Pool(dsn=options.db, size=1, max_size=10, auto_shrink=True, ioloop=IOLoop.current())
    ioloop.run_sync(db.connect)

    bm = Boterator(options.token, db, Burlesque(options.burlesque))
    try:
        ioloop.run_sync(bm.start)
    except:
        bm.stop()

    signal.signal(signal.SIGTERM, bm.stop)
    signal.signal(signal.SIGINT, bm.stop)
