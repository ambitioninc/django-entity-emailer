from os import path

import re
from setuptools import setup, find_packages

# import multiprocessing to avoid this bug (http://bugs.python.org/issue15881#msg170215)
import multiprocessing
assert multiprocessing


def get_version():
    """
    Extracts the version number from the version.py file.
    """
    VERSION_FILE = 'entity_emailer/version.py'
    mo = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', open(VERSION_FILE, 'rt').read(), re.M)
    if mo:
        return mo.group(1)
    else:
        raise RuntimeError('Unable to find version string in {0}.'.format(VERSION_FILE))


def get_requirements(requirements_file):
    """
    Gets a list of requirements from requirements.txt.
    """
    with open(path.join(path.dirname(__file__), 'requirements', requirements_file)) as requirements_file:
        requirements = requirements_file.readlines()

    requirements = [r.strip() for r in requirements if r.strip()]

    return [
        r for r in requirements
        if not r.startswith('#') and not r.startswith('-')
    ]

setup(
    name='django-entity-emailer',
    version=get_version(),
    description='Make emailing users easy and entity-based.',
    long_description=open('README.rst').read(),
    url='https://github.com/ambitioninc/django-entity-emailer',
    author='Erik Swanson',
    author_email='opensource@ambition.com',
    keywords='',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
    ],
    license='MIT',
    install_requires=get_requirements('requirements.txt'),
    tests_require=get_requirements('requirements-testing.txt'),
    test_suite='run_tests.run',
    include_package_data=True,
)
