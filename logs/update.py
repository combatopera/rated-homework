#!/usr/bin/env python3

from pathlib import Path
from subprocess import check_call

def main():
    check_call(['docker', 'compose', 'up', '--build', '-d'], cwd = Path(__file__).parent)

if '__main__' == __name__:
    main()
