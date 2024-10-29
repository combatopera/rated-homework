from aridity.config import ConfigCtrl
from diapyr.util import singleton
from flask import Flask, request
from psycopg import connect

class Application:

    def __init__(self, config):
        self.pgpass = config.pgpass

    def stats(self, customer_id):
        with connect(host = 'db', password = self.pgpass) as conn, conn.cursor() as cur:
            return request.args['from']

@singleton
def application():
    cc = ConfigCtrl()
    cc.load('config.arid')
    app = Application(cc.r)
    flask = Flask(__name__)
    flask.route('/customers/<customer_id>/stats')(app.stats)
    return flask
