from pathlib import Path
from setuptools import find_packages, setup

setup(
    entry_points = dict(console_scripts = ['dbload=dbload:load', 'dbwait=dbload.wait:main', 'dbwipe=dbload:wipe', 'sleep-until-sigint=sleep_until_sigint:main']),
    install_requires = Path('requirements.txt').read_text().splitlines(),
    packages = find_packages(),
    py_modules = ['sleep_until_sigint'],
)
