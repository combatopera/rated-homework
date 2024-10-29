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
from dkrcache.util import iidfile
from lagoon import docker, pyflakes
from lagoon.program import NOEOL, partial
from shutil import copyfileobj
from urllib.parse import quote, quote_plus
from urllib.request import urlopen
from uuid import uuid4
import json

configpath = anchordir / '.share' / 'config.arid'
statepath = builddir / 'state.json'

class Main:

    def check():
        pyflakes[exec](*(p for p in anchordir.glob('**/*.py') if not p.is_relative_to(builddir)))

    def freeze():
        with iidfile() as iid:
            docker.build.__target.freeze[print](*iid.args, anchordir)
            (anchordir / 'api' / 'requirements.txt').write_text(docker.run.__rm(iid.read()))

    def get():
        parser = ArgumentParser()
        parser.add_argument('id')
        parser.add_argument('from')
        args = parser.parse_args()
        port = json.loads(statepath.read_bytes())['port']
        with urlopen(f"http://localhost:{port}/customers/{quote(args.id, '')}/stats?from={quote_plus(getattr(args, 'from'))}") as f:
            copyfileobj(f, sys.stdout.buffer)

    def update():
        if not configpath.exists():
            print('Create config:', configpath, file = sys.stderr)
            configpath.parent.mkdir(exist_ok = True)
            configpath.write_text(f"apache_port = 8000\npgpass = {uuid4()}\n")
        cc = ConfigCtrl()
        cc.load(configpath)
        compose = docker.compose[partial](cwd = anchordir, env = dict(APACHE_PORT = str(cc.r.apache_port), POSTGRES_PASSWORD = cc.r.pgpass))
        compose.up.__build._d[print]()
        info, = docker.inspect[json](compose.ps._q.api[NOEOL]())
        portstr, = {y['HostPort'] for x in info['NetworkSettings']['Ports'].values() for y in x}
        statepath.write_text(json.dumps(dict(port = int(portstr))))

def main():
    getattr(Main, sys.argv.pop(1))() # TODO LATER: Use argparse.

if '__main__' == __name__:
    main()
