from aridity.config import ConfigCtrl
from diapyr.util import singleton
from flask import Flask, request
from psycopg import connect

class Application:

    def __init__(self, config):
        self.pg_host = config.postgres.host
        self.pg_pass = config.postgres.password
        self.pg_user = config.postgres.user

    def stats(self, customer_id):
        with connect(host = self.pg_host, password = self.pg_pass, user = self.pg_user) as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM stats WHERE date >= %s", (request.args['from'],))
            return cur.fetchall()

@singleton
def application():
    cc = ConfigCtrl()
    cc.load('config.arid')
    app = Application(cc.r)
    flask = Flask(__name__)
    flask.add_url_rule('/customers/<customer_id>/stats', view_func = app.stats)
    return flask
