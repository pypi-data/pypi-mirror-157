#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version(*file_paths):
    """Retrieves the version from vocabs/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version("vocabs", "__init__.py")


if sys.argv[-1] == 'publish':
    try:
        import wheel
        print("Wheel version: ", wheel.__version__)
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on git:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')
requirements = [
    'djangorestframework>=3.12.2,<4',
    'acdh-django-browsing>=0.2.0',
    'django-mptt>=0.11.0,<0.15',
    'django-reversion>=3.0.8,<6',
    'rdflib>=5.0.0,<7'
]

setup(
    name='acdh-django-vocabs',
    version=version,
    description="""Curate controlled vocabularies as SKOS""",
    long_description=readme + '\n\n' + history,
    author='Peter Andorfer',
    author_email='peter.andorfer@oeaw.ac.at',
    url='https://github.com/acdh-oeaw/acdh-django-vocabs',
    packages=[
        'vocabs',
    ],
    include_package_data=True,
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    keywords='acdh-django-vocabs',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django :: 3.1',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
