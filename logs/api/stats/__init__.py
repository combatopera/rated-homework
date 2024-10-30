from flask import request
from psycopg import connect
import json

columns = 'successful', 'failed', 'uptime', 'latency_mean', 'latency_median', 'latency_p99'

class Application:

    def __init__(self, config, flask):
        self.pg_host = config.postgres.host
        self.pg_pass = config.postgres.password
        self.pg_user = config.postgres.user
        self.flask = flask

    def stats(self, customer_id):
        with connect(autocommit = True, host = self.pg_host, password = self.pg_pass, user = self.pg_user) as conn, conn.cursor() as cur:
            cur.execute(f"SELECT date, {', '.join(columns)} FROM daily WHERE customer_id = %s AND date >= %s ORDER BY date", (customer_id, request.args['from']))
            return self.flask.response_class(json.dumps({str(date): dict(zip(columns, row)) for date, *row in cur.fetchall()}, separators = (',', ':')), mimetype = 'application/json')
