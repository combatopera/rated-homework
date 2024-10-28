from aridity.config import ConfigCtrl
from diapyr.util import singleton
from flask import Flask, request

class Application:

    def __init__(self, config):
        pass

    def stats(self, customer_id):
        return request.args['from']

@singleton
def application():
    cc = ConfigCtrl()
    app = Application(cc.r)
    flask = Flask(__name__)
    flask.route('/customers/<customer_id>/stats')(app.stats)
    return flask
