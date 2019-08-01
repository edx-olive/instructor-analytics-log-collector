"""Setup file."""

import os

from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='rg_instructor_analytics_log_collector',
    version='2.2.1-web-science',
    install_requires=[
        'setuptools',
        'django-model-utils>=2.3.1,<4',
    ],
    requires=[],
    packages=['rg_instructor_analytics_log_collector'],
    description='Open edX log collector',
    long_description=README,
)
