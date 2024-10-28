from pathlib import Path
from setuptools import find_packages, setup

setup(
    entry_points = dict(console_scripts = ['stats-api=stats.server:main']),
    install_requires = Path('requirements.txt').read_text().splitlines(),
    packages = find_packages(),
)
