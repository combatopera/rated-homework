from aridity.config import ConfigCtrl
from diapyr.util import singleton
from flask import Flask, request
from psycopg import connect

class Application:

    cols = 'successful', 'failed', 'latency_mean', 'latency_median', 'latency_p99'

    def __init__(self, config):
        self.pg_host = config.postgres.host
        self.pg_pass = config.postgres.password
        self.pg_user = config.postgres.user

    def stats(self, customer_id):
        with connect(host = self.pg_host, password = self.pg_pass, user = self.pg_user) as conn, conn.cursor() as cur:
            cur.execute(f"SELECT date, {', '.join(self.cols)} FROM stats WHERE customer_id = %s AND date >= %s ORDER BY date", (customer_id, request.args['from']))
            return {str(date): dict(zip(self.cols, row)) for date, *row in cur.fetchall()} # XXX: Preserve key order?

@singleton
def application():
    cc = ConfigCtrl()
    cc.load('config.arid')
    app = Application(cc.r)
    flask = Flask(__name__)
    flask.add_url_rule('/customers/<customer_id>/stats', view_func = app.stats)
    return flask
