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
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
    ],
    license='MIT',
    install_requires=[
        'beautifulsoup4>=4.3.2',
        'Django>=2.0',
        'django-db-mutex>=1.2.0',
        'django-entity>=4.2.0',
        'django-entity-event>=1.2.0',
        'ambition-django-uuidfield>=0.5.0',
    ],
    tests_require=[
        'django-dynamic-fixture',
        'django-nose>=1.4',
        'freezegun',
        'mock',
    ],
    test_suite='run_tests.run_tests',
    include_package_data=True,
)
