from aridity.config import ConfigCtrl
from lagoon import mod_wsgi_express

def main():
    cc = ConfigCtrl()
    cc.load('config.arid')
    mod_wsgi_express.start_server.__log_to_terminal.__application_type.module[exec]('--port', cc.r.apache_port, 'stats.app')
