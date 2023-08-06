==========
iterstring
==========


.. image:: https://img.shields.io/pypi/v/iterstring.svg
        :target: https://pypi.python.org/pypi/iterstring

.. image:: https://img.shields.io/travis/datagazing/iterstring.svg
        :target: https://travis-ci.com/datagazing/iterstring

.. image:: https://readthedocs.org/projects/iterstring/badge/?version=latest
        :target: https://iterstring.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status


Simple class that allows writing lists and dicts as heredoc strings

* Write lists as strings with one line per element
* Same for dictionaries, but use first token on each line as key

Features
--------

* Handles comments (using # characters)
* Strips away extraneous whitespace with reasonable defaults (configurable)
* Coerce items to numbers where possible (see coerce)
* Iterating over the object treats it like a list
* Indexing the object treats it like a dictionary
* listr and distr helper functions provide simple interfaces

Examples
--------

A simple use case:

.. code-block:: python

  >>> from iterstring import listr # or distr
  >>> some_list = listr('''
  item one # with a comment
    2
  three
  ''')
  >>> some_list
  ['item one', 2, 'three']
  >>> type(some_list)
  <class 'list'>

Using the class directly:

.. code-block:: python

  >>> from iterstring import Istr
  >>> asdf = Istr('''
  item one # with a comment
    2
  three
  ''')
  >>> asdf.to_list()
  ['item one', 2, 'three']
  >>> type(asdf)
  <class 'iterstring.Istr'>

  >>> [x for x in asdf]
  ['item one', 2, 'three']

  >>> fdsa = Istr('''
  item one # with a comment
    2 some other value
  key3 3.14159
  ''')
  >>> asdf.to_dict()
  {'item': 'one', 2: 'some other value', 'key3': 3.14159}
  >>> asdf.to_dict(coerce=False)
  {'item': 'one', '2': 'some other value', 'key3': '3.14159'}

License
-------

* Free software: MIT license

Documentation
-------------

* https://iterstring.readthedocs.io/

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
