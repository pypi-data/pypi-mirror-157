import setuptools
from pathlib import Path

setuptools.setup(
    name='tayopdf',
    long_description=Path('README.md').read_text(),
    version=1.0,
    packages=setuptools.find_packages(exclude=['test', 'data'])
)
