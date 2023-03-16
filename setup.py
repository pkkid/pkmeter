#!/usr/bin/python3
# -*- coding: utf-8 -*-
from distutils.core import setup
from pip.req import parse_requirements
from setuptools import find_packages

requirements = [str(line.req) for line in parse_requirements('requirements.txt')]

setup(
    name='pkmeter',
    version='1.0',
    description='Desktop system monitors written in Python',
    author='pkkid',
    author_email='',
    url='https://github.com/pkkid/pkmeter',
    packages=find_packages(),
    scripts=['pkmeter.py'],
    install_requires=requirements,
    long_description=open('README.txt').read()
)
