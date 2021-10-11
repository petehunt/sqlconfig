from setuptools import find_packages, setup
import os

with open(os.path.join(os.path.dirname(__file__), "README.md"), "r") as f:
  README = f.read()

setup(
    name='sqlconfig',
    version=0.1,
    packages=find_packages(exclude=["sqlconfig.tests"]),
    entry_points={'console_scripts': ['sqlconfig = sqlconfig.cli:main']},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Database",
    ],
    author="Pete Hunt",
    author_email="floydophone@gmail.com",
    description="Use SQLite to manage your configs",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/petehunt/sqlconfig",
    license="MIT",
    python_requires='>=3',
)