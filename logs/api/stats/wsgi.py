from . import Application
from aridity.config import ConfigCtrl
from diapyr.util import singleton
from flask import Flask

@singleton
def application():
    cc = ConfigCtrl()
    cc.load('config.arid')
    flask = Flask(__name__)
    app = Application(cc.r, flask)
    flask.add_url_rule('/customers/<customer_id>/stats', view_func = app.stats)
    return flask
