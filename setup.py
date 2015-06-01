#!/usr/bin/python3

from distutils.core import setup
from pip.req import parse_requirements
from setuptools import find_packages

requirements = [str(line.req) for line in parse_requirements('requirements.pip')]

setup(
    name='pkmeter',
    version='1.0',
    description='QT-based meters and gadgets for your desktop!',
    author='pkkid',
    author_email='',
    url='http://bitbucket.org/mjs7231/pkmeter',
    packages=find_packages(),
    scripts=['pkmeter'],
    install_requires=requirements,
    long_description=open('README.txt').read()
)
