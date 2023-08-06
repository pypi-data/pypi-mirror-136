Temporary PostgreSQL databases for Django and pytest
====================================================

Use case
--------

This pytest plugin can be used to test a Django application that uses
PostgreSQL. It leverages the `testing.postgresql`_ module to setup a
temporary PostgreSQL database server and injects the configuration for it
into Django's settings. It is intended to be used together with
`pytest-django`_.

Requirements
------------

`testing.postgresql`_ needs the postgresql server binary available.

How to use
----------

To use, simply install the package in your testing environment and laod
the `django-testing-psotgresql` plugin when running pytest (pytest normally
auto-discovers it).

The plugin re-uses the configuration used by `pytest-django`_.

By default, only the ``default`` database is setup. You can modify this
by setting ``PYTEST_SETUP_DATABASES`` to a list of database aliases in
your ``settings`` module. The list can contain strings, or tuples if you
want some aliases to share the same database backend.

.. _testing.postgresql: https://pypi.org/project/testing.postgresql/
.. _pytest-django: https://pypi.org/project/pytest-django/
