from pathlib import Path
from setuptools import find_packages, setup

setup(
    install_requires = Path('requirements.txt').read_text().splitlines(),
    packages = find_packages(),
)
