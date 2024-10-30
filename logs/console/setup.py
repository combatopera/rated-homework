from pathlib import Path
from setuptools import find_packages, setup

setup(
    entry_points = dict(console_scripts = ['dbload=dbload:load', 'dbwait=dbload.wait:main', 'dbwipe=dbload:wipe']),
    install_requires = Path('requirements.txt').read_text().splitlines(),
    packages = find_packages(),
)
