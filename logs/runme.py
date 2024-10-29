#!/usr/bin/env python3

def _equipifnecessary():
    from shutil import copy2
    from subprocess import check_call
    import os, sys
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
    try:
        ok = journalpath.read_bytes() == requirementspath.read_bytes()
    except FileNotFoundError:
        ok = False
    if not ok:
        print('Create/update venv:', venvpath, file = sys.stderr)
        check_call([sys.executable, '-m', 'venv', venvpath])
        check_call([venvpath / 'bin' / 'pip', 'install', '-r', requirementspath])
        copy2(requirementspath, journalpath)
    args = [venvpath / 'bin' / 'python', __file__, token, *sys.argv[1:]]
    os.execv(args[0], args)

from pathlib import Path
anchordir = Path(__file__).parent
builddir = anchordir / '.build'
if '__main__' == __name__:
    _equipifnecessary()
from argparse import ArgumentParser
from dkrcache.util import iidfile
from lagoon import docker
from lagoon.program import NOEOL
from shutil import copyfileobj
from urllib.parse import quote, quote_plus
from urllib.request import urlopen
import json, sys

class Main:

    def freeze():
        apidir = anchordir / 'api'
        with iidfile() as iid:
            docker.build.__target.freeze[print](*iid.args, apidir)
            (apidir / 'requirements.txt').write_text(docker.run.__rm(iid.read()))

    def get():
        parser = ArgumentParser()
        parser.add_argument('id')
        parser.add_argument('from')
        args = parser.parse_args()
        port = json.loads((builddir / 'info.json').read_bytes())['port']
        with urlopen(f"http://localhost:{port}/customers/{quote(args.id, '')}/stats?from={quote_plus(getattr(args, 'from'))}") as f:
            copyfileobj(f, sys.stdout.buffer)

    def update():
        docker.compose.up.__build._d[print](cwd = anchordir)
        info, = docker.inspect[json](docker.compose.ps._q.api[NOEOL](cwd = anchordir))
        portstr, = {y['HostPort'] for x in info['NetworkSettings']['Ports'].values() for y in x}
        (builddir / 'info.json').write_text(json.dumps(dict(port = int(portstr))))

def main():
    getattr(Main, sys.argv.pop(1))() # TODO LATER: Use argparse.

if '__main__' == __name__:
    main()
