#!/usr/bin/env python3

from setuptools import setup

# manually read version from file
exec(open("expsweep/version.py").read())

setup(
    name='expsweep',
    version=version,
    packages=['expsweep'],
    author="Evan Widloski",
    author_email="evan@evanw.org",
    description="sweep numerical experiment parameters and collect results in a Pandas table",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license="MIT",
    keywords="pandas pqdm",
    url="https://github.com/evidlo/expsweep",
    install_requires=[
        "pqdm",
        "pandas",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
    ]
)
