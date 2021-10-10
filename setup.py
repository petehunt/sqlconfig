from setuptools import find_packages, setup

setup(
    name='sqlconfig',
    version=0.1,
    packages=find_packages(exclude=["sqlconfig.tests"]),
    entry_points={'console_scripts': ['sqlconfig = sqlconfig.cli:main']},
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    author="Pete Hunt",
    author_email="floydophone@gmail.com",
    description="Use SQLite to manage your configs",
    url="https://github.com/petehunt/sqlconfig",
    license="MIT",
)