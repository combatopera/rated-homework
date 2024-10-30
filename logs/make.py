#!/usr/bin/env python3

from pathlib import Path
from venvpool import initlogging
import logging, sys

def _activateifnecessary():
    from shutil import copy2
    from subprocess import check_call
    import os
    initlogging()
    indicator = '--venv'
    indicatorindex = 1
    if indicatorindex < len(sys.argv) and indicator == sys.argv[indicatorindex]:
        sys.argv.pop(indicatorindex)
        return
    requirementspath = anchordir / 'requirements.txt'
    venvdir = builddir / 'venv'
    journalpath = venvdir / 'journal'
    bindir = venvdir / 'bin'
    if not (journalpath.exists() and journalpath.read_bytes() == requirementspath.read_bytes()):
        log.info("Create/update venv: %s", venvdir)
        check_call([sys.executable, '-m', 'venv', venvdir])
        check_call([bindir / 'pip', 'install', '-r', requirementspath])
        copy2(requirementspath, journalpath)
    argv = bindir / 'python', __file__, indicator, *sys.argv[1:]
    os.execve(argv[0], argv, dict(os.environ, PATH = f"{bindir}{os.pathsep}{os.environ['PATH']}"))

log = logging.getLogger(__name__)
anchordir = Path(__file__).parent
builddir = anchordir / '.build'
if '__main__' == __name__:
    _activateifnecessary()

from argparse import ArgumentParser
from aridity.config import ConfigCtrl
from diapyr.util import invokeall
from dkrcache.util import iidfile
from lagoon import docker, pyflakes
from lagoon.program import NOEOL, partial
from shutil import copyfileobj, rmtree
from urllib.parse import quote, quote_plus
from urllib.request import urlopen
from uuid import uuid4
import json

configpath = anchordir / 'etc' / 'config.arid'
portpath = builddir / 'port'

class Main:

    def __init__(self, config):
        self.docker_compose = docker.compose[partial](cwd = anchordir, env = dict(APACHE_PORT = str(config.apache_port), POSTGRES_PASSWORD = config.postgres.password, POSTGRES_USER = config.postgres.user))

    def _test(self):
        pyflakes[print](*(p for p in anchordir.glob('**/*.py') if not p.is_relative_to(builddir)))
        invokeall([docker.build.__target.test[print, partial]('--build-arg', f"service={service}", anchordir) for service in ['api', 'console']])

    def compose(self):
        self.docker_compose[exec](*sys.argv[2:])

    def freeze(self):
        parser = ArgumentParser()
        parser.add_argument('goal', choices = ['freeze'])
        parser.add_argument('service')
        service = parser.parse_args().service
        with iidfile() as iid:
            docker.build.__target.freeze[print]('--build-arg', f"service={service}", *iid.args, anchordir)
            (anchordir / service / 'requirements.txt').write_text(docker.run.__rm(iid.read()))

    def get(self):
        parser = ArgumentParser()
        parser.add_argument('goal', choices = ['get'])
        parser.add_argument('--raw', action = 'store_true')
        parser.add_argument('id')
        parser.add_argument('from')
        args = parser.parse_args()
        with urlopen(f"http://localhost:{portpath.read_text().rstrip()}/customers/{quote(args.id, '')}/stats?from={quote_plus(getattr(args, 'from'))}") as f:
            copyfileobj(f, sys.stdout.buffer) if args.raw else print(json.dumps(json.load(f), indent = 4))

    def load(self):
        parser = ArgumentParser()
        parser.add_argument('goal', choices = ['load'])
        parser.add_argument('logpath', type = Path)
        args = parser.parse_args()
        self._update()
        with args.logpath.open() as f:
            self.docker_compose.exec._T.console.dbload[print](stdin = f)

    def scrub(self):
        self.docker_compose.down[print]()
        log.info("Delete: %s", configpath)
        configpath.unlink()
        log.info("Delete: %s", builddir)
        rmtree(builddir)

    def _update(self):
        self._test()
        self.docker_compose.up.__build._d[print]()
        info, = docker.inspect[json](self.docker_compose.ps._q.api[NOEOL]())
        portstr, = {y['HostPort'] for x in info['NetworkSettings']['Ports'].values() for y in x}
        portpath.write_text(f"{portstr}\n")
        self.docker_compose.exec.console.dbwait[print]()

    def wipe(self):
        self._update()
        self.docker_compose.exec.console.dbwipe[print]()

def main():
    if not configpath.exists():
        log.info("Create config: %s", configpath)
        configpath.write_text(f". $./(root.arid)\npostgres password = {uuid4()}\n")
    cc = ConfigCtrl()
    cc.load(configpath)
    getattr(Main(cc.r), sys.argv[1])()

if '__main__' == __name__:
    main()
