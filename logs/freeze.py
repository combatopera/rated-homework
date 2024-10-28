#!/usr/bin/env python3

from pathlib import Path
from subprocess import check_output

def main():
    apidir = Path(__file__).parent / 'api'
    image = check_output(['docker', 'build', '-q', '--target', 'freeze', apidir]).rstrip()
    (apidir / 'requirements.txt').write_bytes(check_output(['docker', 'run', '--rm', image]))

if '__main__' == __name__:
    main()
