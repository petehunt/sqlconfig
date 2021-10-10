from setuptools import setup

setup(
    name='sqlconfig',
    version=0.1,
    packages=['sqlconfig'],
    entry_points={'console_scripts': ['sqlconfig = sqlconfig.cli:main']}
)