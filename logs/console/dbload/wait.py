from aridity.config import ConfigCtrl
from psycopg import connect, OperationalError
from venvpool import initlogging
import logging, time

log = logging.getLogger(__name__)
sleeptime = .5

def main():
    initlogging()
    cc = ConfigCtrl()
    cc.load('config.arid')
    while True:
        try:
            with connect(host = cc.r.postgres.host, password = cc.r.postgres.password, user = cc.r.postgres.user):
                log.info('Connect now possible.')
                break
        except OperationalError as e:
            log.debug("Retry after %s seconds: %s", sleeptime, e)
        time.sleep(sleeptime)
