"""Setup file."""

import os
import re

from setuptools import setup


def get_version(*file_paths):
    """
    Extract the version string from the file at the given relative path fragments.
    """
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


VERSION = get_version('rg_instructor_analytics_log_collector', '__init__.py')

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

with open(os.path.join(os.path.dirname(__file__), 'CHANGELOG.rst')) as changelog:
    CHANGELOG = changelog.read()

def load_requirements(*requirements_paths):
    """
    Load all requirements from the specified requirements files.

    Returns a list of requirement strings.
    """
    requirements = set()
    for path in requirements_paths:
        requirements.update(
            line.split('#')[0].strip() for line in open(path).readlines()
            if is_requirement(line.strip())
        )
    return list(requirements)


def is_requirement(line):
    """
    Return True if the requirement line is a package requirement;

    that is, it is not blank, a comment, a URL, or an included file.
    """
    return not (line == '' or line.startswith(('-r', '#', '-e', 'git+', '-c')))


setup(
    name='instructor-analytics-log-collector',
    version=VERSION,
    install_requires=load_requirements("requirements.txt"),
    requires=[],
    packages=['rg_instructor_analytics_log_collector'],
    description='Open edX log collector',
    long_description=README + '\n\n' + CHANGELOG,
    entry_points={
        "lms.djangoapp": [
            "rg_ia_log_collector = rg_instructor_analytics_log_collector.apps:RgIALogCollectorAppConfig",
        ],
    }
)
