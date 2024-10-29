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
    requirementspath = contextdir / 'requirements.txt'
    venvpath = contextdir / '.build' / 'venv'
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
contextdir = Path(__file__).parent
if '__main__' == __name__:
    _equipifnecessary()
from lagoon import docker
from lagoon.program import NOEOL
import sys

def freeze():
    apidir = contextdir / 'api'
    (apidir / 'requirements.txt').write_text(docker.run.__rm(docker.build._q.__target.freeze[NOEOL](apidir))) # TODO: Show logging.

def update():
    docker.compose.up.__build._d[print](cwd = contextdir)

def main():
    globals()[sys.argv.pop(1)]()

if '__main__' == __name__:
    main()
