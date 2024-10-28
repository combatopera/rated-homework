#!/usr/bin/env python3

from argparse import ArgumentParser
from pathlib import Path
from shutil import copyfileobj
from subprocess import check_output
from urllib.parse import quote, quote_plus
from urllib.request import urlopen
import json, sys

def main():
    parser = ArgumentParser()
    parser.add_argument('id')
    parser.add_argument('from')
    args = parser.parse_args()
    container = check_output(['docker', 'compose', 'ps', '-q', 'api'], cwd = Path(__file__).parent).rstrip()
    info, = json.loads(check_output(['docker', 'inspect', container]))
    portstr, = {y['HostPort'] for x in info['NetworkSettings']['Ports'].values() for y in x}
    with urlopen(f"http://localhost:{portstr}/customers/{quote(args.id, '')}/stats?from={quote_plus(getattr(args, 'from'))}") as f:
        copyfileobj(f, sys.stdout.buffer)

if '__main__' == __name__:
    main()
