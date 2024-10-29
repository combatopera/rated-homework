#!/usr/bin/env python3

from pathlib import Path
import logging, sys

def _equipifnecessary():
    from shutil import copy2
    from subprocess import check_call
    import os
    logging.basicConfig(format = "%(asctime)s %(levelname)s %(message)s", level = logging.DEBUG)
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
        log.info("Create/update venv: %s", venvpath)
        check_call([sys.executable, '-m', 'venv', venvpath])
        check_call([bindir / 'pip', 'install', '-r', requirementspath])
        copy2(requirementspath, journalpath)
    args = [venvpath / 'bin' / 'python', __file__, token, *sys.argv[1:]]
    os.execve(args[0], args, dict(os.environ, PATH = f"{bindir}{os.pathsep}{os.environ['PATH']}"))

log = logging.getLogger(__name__)
anchordir = Path(__file__).parent
builddir = anchordir / '.build'
if '__main__' == __name__:
    _equipifnecessary()

from argparse import ArgumentParser
from aridity.config import ConfigCtrl
from dkrcache.util import iidfile
from lagoon import docker, pyflakes
from lagoon.program import NOEOL, partial
from shutil import copyfileobj
from urllib.parse import quote, quote_plus
from urllib.request import urlopen
from uuid import uuid4
import json

configpath = anchordir / 'etc' / 'config.arid'
statepath = builddir / 'state.json'

class Main:

    def __init__(self, config):
        self.docker_compose = docker.compose[partial](cwd = anchordir, env = dict(APACHE_PORT = str(config.apache_port), POSTGRES_PASSWORD = config.postgres.password, POSTGRES_USER = config.postgres.user))

    def check(self):
        pyflakes[exec](*(p for p in anchordir.glob('**/*.py') if not p.is_relative_to(builddir)))

    def compose(self):
        self.docker_compose[exec](*sys.argv[1:])

    def freeze(self):
        parser = ArgumentParser()
        parser.add_argument('service')
        service = parser.parse_args().service
        with iidfile() as iid:
            docker.build.__target.freeze[print]('--build-arg', f"service={service}", *iid.args, anchordir)
            (anchordir / service / 'requirements.txt').write_text(docker.run.__rm(iid.read()))

    def get(self):
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

    def load(self):
        parser = ArgumentParser()
        parser.add_argument('logpath', type = Path)
        args = parser.parse_args()
        with args.logpath.open() as f:
            self.docker_compose.exec._T.console.dbload[print](stdin = f)

    def update(self):
        def serviceport(service):
            info, = docker.inspect[json](self.docker_compose.ps._q[NOEOL](service))
            portstr, = {y['HostPort'] for x in info['NetworkSettings']['Ports'].values() for y in x}
            return int(portstr)
        self.docker_compose.up.__build._d[print]()
        statepath.write_text(json.dumps(dict(port = {s: serviceport(s) for s in ['api']})))

def main():
    if not configpath.exists():
        log.info("Create config: %s", configpath)
        configpath.write_text(f". $./(root.arid)\npostgres password = {uuid4()}\n")
    cc = ConfigCtrl()
    cc.load(configpath)
    getattr(Main(cc.r), sys.argv.pop(1))() # TODO LATER: Use argparse.

if '__main__' == __name__:
    main()
