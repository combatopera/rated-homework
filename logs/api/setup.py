from pathlib import Path
from setuptools import find_packages, setup

setup(
    packages = find_packages(),
    install_requires = Path('requirements.txt').read_text().splitlines(),
)
