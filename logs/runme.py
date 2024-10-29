#!/usr/bin/env python3

from pathlib import Path
import sys

def _equipifnecessary():
    from shutil import copy2
    from subprocess import check_call
    import os
    token = '--venv'
    tokenindex = 1
    try:
        equipped = token == sys.argv[tokenindex]
    except IndexError:
        equipped = False
    if equipped:
        sys.argv.pop(tokenindex)
        return
    requirementspath = anchordir / 'requirements.txt'
    venvpath = builddir / 'venv'
    journalpath = venvpath / 'journal'
    bindir = venvpath / 'bin'
    try:
        ok = journalpath.read_bytes() == requirementspath.read_bytes()
    except FileNotFoundError:
        ok = False
    if not ok:
        print('Create/update venv:', venvpath, file = sys.stderr)
        check_call([sys.executable, '-m', 'venv', venvpath])
        check_call([bindir / 'pip', 'install', '-r', requirementspath])
        copy2(requirementspath, journalpath)
    args = [venvpath / 'bin' / 'python', __file__, token, *sys.argv[1:]]
    os.execve(args[0], args, dict(os.environ, PATH = f"{bindir}{os.pathsep}{os.environ['PATH']}"))

anchordir = Path(__file__).parent
builddir = anchordir / '.build'
if '__main__' == __name__:
    _equipifnecessary()

from argparse import ArgumentParser
from aridity.config import ConfigCtrl
from collections import defaultdict
from dkrcache.util import iidfile
from lagoon import docker, pyflakes
from lagoon.program import NOEOL, partial
from psycopg import connect
from shutil import copyfileobj
from urllib.parse import quote, quote_plus
from urllib.request import urlopen
from uuid import uuid4
import json, numpy as np

configpath = anchordir / '.share' / 'config.arid'
statepath = builddir / 'state.json'

class Day:

    classification = {2: 'successful', 4: 'failed', 5: 'failed'}
    successful = 0
    failed = 0

    def __init__(self):
        self.durations = []

    def put(self, status_code, duration):
        k = self.classification[status_code // 100]
        setattr(self, k, getattr(self, k) + 1)
        self.durations.append(duration) # XXX: Exclude any status?

    def latency_mean(self):
        return np.mean(self.durations)

    def latency_percentiles(self, *percentiles):
        return np.percentile(self.durations, percentiles)

class Main:

    def check():
        pyflakes[exec](*(p for p in anchordir.glob('**/*.py') if not p.is_relative_to(builddir)))

    def freeze():
        with iidfile() as iid:
            docker.build.__target.freeze[print](*iid.args, anchordir)
            (anchordir / 'api' / 'requirements.txt').write_text(docker.run.__rm(iid.read()))

    def get():
        parser = ArgumentParser()
        parser.add_argument('--raw', action = 'store_true')
        parser.add_argument('id')
        parser.add_argument('from')
        args = parser.parse_args()
        port = json.loads(statepath.read_bytes())['port']['api']
        with urlopen(f"http://localhost:{port}/customers/{quote(args.id, '')}/stats?from={quote_plus(getattr(args, 'from'))}") as f:
            if args.raw:
                copyfileobj(f, sys.stdout.buffer)
            else:
                print(json.dumps(json.load(f), indent = 4))

    def load():
        parser = ArgumentParser()
        parser.add_argument('logpath', type = Path)
        args = parser.parse_args()
        cc = ConfigCtrl()
        cc.load(configpath)
        # XXX: Use autocommit?
        with connect(host = 'localhost', password = cc.r.postgres.password, port = json.loads(statepath.read_bytes())['port']['db'], user = cc.r.postgres.user) as conn, conn.cursor() as cur:
            cur.execute('DROP INDEX IF EXISTS customer_date')
            cur.execute('DROP TABLE IF EXISTS stats')
            cur.execute('CREATE TABLE stats (customer_id text NOT NULL, date date NOT NULL, successful integer NOT NULL, failed integer NOT NULL, latency_mean real NOT NULL, latency_median real NOT NULL, latency_p99 real NOT NULL)')
            cur.execute('CREATE UNIQUE INDEX customer_date ON stats (customer_id, date)') # XXX: Create after load?
            days = defaultdict(Day)
            with args.logpath.open() as f:
                for line in f:
                    date, time, customer_id, request_path, status_code, duration = line.split()
                    days[customer_id, date].put(int(status_code), float(duration))
            for (customer_id, date), day in days.items():
                cur.execute('INSERT INTO stats VALUES (%s, %s, %s, %s, %s, %s, %s)', (customer_id, date, day.successful, day.failed, day.latency_mean(), *day.latency_percentiles(50, 99)))

    def update():
        def serviceport(service):
            info, = docker.inspect[json](compose.ps._q[NOEOL](service))
            portstr, = {y['HostPort'] for x in info['NetworkSettings']['Ports'].values() for y in x}
            return int(portstr)
        if not configpath.exists():
            print('Create config:', configpath, file = sys.stderr)
            configpath.parent.mkdir(exist_ok = True)
            configpath.write_text(f"""apache_port = 8000
postgres
    host = db
    password = {uuid4()}
    user = postgres
""")
        cc = ConfigCtrl()
        cc.load(configpath)
        compose = docker.compose[partial](cwd = anchordir, env = dict(APACHE_PORT = str(cc.r.apache_port), POSTGRES_PASSWORD = cc.r.postgres.password, POSTGRES_USER = cc.r.postgres.user))
        compose.up.__build._d[print]()
        statepath.write_text(json.dumps(dict(port = {s: serviceport(s) for s in ['api', 'db']})))

def main():
    getattr(Main, sys.argv.pop(1))() # TODO LATER: Use argparse.

if '__main__' == __name__:
    main()
