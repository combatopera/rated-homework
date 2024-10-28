from diapyr.util import singleton
from flask import Flask, request

class Application:

    def stats(self, customer_id):
        return request.args['from']

@singleton
def application():
    app = Application()
    flask = Flask(__name__)
    flask.route('/customers/<customer_id>/stats')(app.stats)
    return flask
