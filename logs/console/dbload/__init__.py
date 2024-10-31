from .algo import UptimeEstimator
from aridity.config import ConfigCtrl
from collections import defaultdict
from datetime import time
from psycopg import connect
from venvpool import initlogging
import logging, numpy as np, sys

log = logging.getLogger(__name__)

class Day:

    outage_class = 5
    class_to_tally = {2: 'successful', 4: 'failed', outage_class: 'failed'}
    successful = 0
    failed = 0

    def __init__(self):
        self.uptime_estimator = UptimeEstimator()
        self.durations = []

    def put(self, time, status_code, duration):
        status_class = status_code // 100
        tally = self.class_to_tally[status_class]
        setattr(self, tally, getattr(self, tally) + 1)
        self.uptime_estimator.add(time, self.outage_class != status_class)
        self.durations.append(duration) # XXX: Filter status?

    def uptime(self):
        return self.uptime_estimator.uptime()

    def latency_mean(self):
        return np.mean(self.durations)

    def latency_percentiles(self, *percentiles):
        return np.percentile(self.durations, percentiles)

def load():
    initlogging()
    cc = ConfigCtrl()
    cc.load('config.arid')
    log.info('Read data.')
    days = defaultdict(Day)
    for line in sys.stdin:
        isodate, isotime, customer_id, request_path, status_code, duration = line.split()
        days[customer_id, isodate].put(time.fromisoformat(isotime), int(status_code), float(duration))
    with connect(host = cc.r.postgres.host, password = cc.r.postgres.password, user = cc.r.postgres.user) as conn, conn.cursor() as cur:
        log.info('Create table.')
        cur.execute('CREATE TABLE daily (customer_id text NOT NULL, date date NOT NULL, successful integer NOT NULL, failed integer NOT NULL, uptime real NOT NULL, latency_mean real NOT NULL, latency_median real NOT NULL, latency_p99 real NOT NULL)')
        log.info('Insert data.')
        for (customer_id, isodate), day in days.items():
            cur.execute("INSERT INTO daily VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (customer_id, isodate, day.successful, day.failed, day.uptime(), day.latency_mean(), *day.latency_percentiles(50, 99)))
        cur.execute('CREATE UNIQUE INDEX customer_date ON daily (customer_id, date)')

def wipe():
    initlogging()
    cc = ConfigCtrl()
    cc.load('config.arid')
    with connect(host = cc.r.postgres.host, password = cc.r.postgres.password, user = cc.r.postgres.user) as conn, conn.cursor() as cur:
        log.info('Drop resources.')
        cur.execute('DROP INDEX IF EXISTS customer_date')
        cur.execute('DROP TABLE IF EXISTS daily')
