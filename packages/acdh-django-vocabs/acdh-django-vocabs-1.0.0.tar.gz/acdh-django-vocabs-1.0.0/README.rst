=============================
ACDH Django Vocabs
=============================

.. image:: https://badge.fury.io/py/acdh-django-vocabs.svg
    :target: https://badge.fury.io/py/acdh-django-vocabs

.. image:: https://api.travis-ci.com/acdh-oeaw/acdh-django-vocabs.svg?branch=master
    :target: https://travis-ci.com/github/acdh-oeaw/acdh-django-vocabs

.. image:: https://codecov.io/gh/acdh-oeaw/acdh-django-vocabs/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/acdh-oeaw/acdh-django-vocabs

Curate controlled vocabularies as SKOS

Documentation
-------------

The full documentation is at https://acdh-django-vocabs.readthedocs.io.

Quickstart
----------

Install ACDH Django Vocabs::

    pip install acdh-django-vocabs

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'vocabs.apps.VocabsConfig',
        ...
    )

Add ACDH Django Vocabs's URL patterns:

.. code-block:: python

    from vocabs import urls as vocabs_urls


    urlpatterns = [
        ...
        url(r'^', include(vocabs_urls)),
        ...
    ]

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox


Development commands
---------------------

::

    pip install -r requirements_dev.txt
    invoke -l


Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage


rm -rf ./dist
python setup.py sdist bdist_wheel
twine upload dist/*