Springboard IoGT
================

.. image:: https://travis-ci.org/universalcore/springboard-iogt.svg?branch=develop
    :target: https://travis-ci.org/universalcore/springboard-iogt
    :alt: Continuous Integration

.. image:: https://coveralls.io/repos/universalcore/springboard-iogt/badge.png?branch=develop
    :target: https://coveralls.io/r/universalcore/springboard-iogt?branch=develop
    :alt: Code Coverage

.. image:: https://readthedocs.org/projects/springboard/badge/?version=latest
    :target: https://springboard.readthedocs.org
    :alt: Springboard Documentation

Installing for local dev
~~~~~~~~~~~~~~~~~~~~~~~~

Make sure elasticsearch_ is running, then::

    $ git clone https://github.com/universalcore/springboard-iogt.git
    $ cd springboard-iogt
    $ virtualenv ve
    $ source ve/bin/activate
    (ve)$ pip install -e .
    (ve)$ springboard bootstrap -v
    (ve)$ pserve development.ini --reload


.. _elasticsearch: http://www.elasticsearch.org
