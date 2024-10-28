from flask import Flask

application = Flask(__name__)

@application.route('/customers/<customer_id>/stats')
def stats(customer_id):
    pass
