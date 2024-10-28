from flask import Flask, request

application = Flask(__name__)

@application.route('/customers/<customer_id>/stats')
def stats(customer_id):
    return request.args['from']
