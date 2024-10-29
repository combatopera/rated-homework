from aridity.config import ConfigCtrl
from collections import defaultdict
from psycopg import connect
import numpy as np, sys

class Day:

    classification = {2: 'successful', 4: 'failed', 5: 'failed'}
    successful = 0
    failed = 0

    def __init__(self):
        self.durations = []

    def put(self, status_code, duration):
        k = self.classification[status_code // 100]
        setattr(self, k, getattr(self, k) + 1)
        self.durations.append(duration) # XXX: Exclude any status?

    def latency_mean(self):
        return np.mean(self.durations)

    def latency_percentiles(self, *percentiles):
        return np.percentile(self.durations, percentiles)

def main():
    cc = ConfigCtrl()
    cc.load('config.arid')
    # XXX: Use autocommit?
    with connect(host = cc.r.postgres.host, password = cc.r.postgres.password, user = cc.r.postgres.user) as conn, conn.cursor() as cur:
        cur.execute('DROP INDEX IF EXISTS customer_date')
        cur.execute('DROP TABLE IF EXISTS stats')
        cur.execute('CREATE TABLE stats (customer_id text NOT NULL, date date NOT NULL, successful integer NOT NULL, failed integer NOT NULL, latency_mean real NOT NULL, latency_median real NOT NULL, latency_p99 real NOT NULL)')
        cur.execute('CREATE UNIQUE INDEX customer_date ON stats (customer_id, date)') # XXX: Create after load?
        days = defaultdict(Day)
        for line in sys.stdin:
            date, time, customer_id, request_path, status_code, duration = line.split()
            days[customer_id, date].put(int(status_code), float(duration))
        for (customer_id, date), day in days.items():
            cur.execute('INSERT INTO stats VALUES (%s, %s, %s, %s, %s, %s, %s)', (customer_id, date, day.successful, day.failed, day.latency_mean(), *day.latency_percentiles(50, 99)))

if '__main__' == __name__:
    main()
