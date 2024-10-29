from aridity.config import ConfigCtrl
from diapyr.util import singleton
from flask import Flask, request
from psycopg import connect
import json

class Application:

    cols = 'successful', 'failed', 'latency_mean', 'latency_median', 'latency_p99'

    def __init__(self, config, flask):
        self.pg_host = config.postgres.host
        self.pg_pass = config.postgres.password
        self.pg_user = config.postgres.user
        self.flask = flask

    def stats(self, customer_id):
        with connect(host = self.pg_host, password = self.pg_pass, user = self.pg_user) as conn, conn.cursor() as cur:
            cur.execute(f"SELECT date, {', '.join(self.cols)} FROM stats WHERE customer_id = %s AND date >= %s ORDER BY date", (customer_id, request.args['from']))
            return self.flask.response_class(json.dumps({str(date): dict(zip(self.cols, row)) for date, *row in cur.fetchall()}, separators = (',', ':')), mimetype = 'application/json')

@singleton
def application():
    cc = ConfigCtrl()
    cc.load('config.arid')
    flask = Flask(__name__)
    app = Application(cc.r, flask)
    flask.add_url_rule('/customers/<customer_id>/stats', view_func = app.stats)
    return flask
