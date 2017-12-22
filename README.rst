pyreds
======

.. image:: https://travis-ci.org/7anshuai/pyreds.svg?branch=master
    :target: https://travis-ci.org/7anshuai/pyreds

`reds <https://github.com/tj/reds>`_ is a light-weight Redis Search for Node.js.

pyreds is a Python port of reds.

Installation
------------

pyreds requires a running Redis server. See `Redis's quickstart
<http://redis.io/topics/quickstart>`_ for installation instructions.

To install pyreds, simply:

.. code-block:: bash

    $ pip install pyreds

You may need install NLTK Data:

.. code-block:: pycon

    >>> import nltk
    >>> nltk.download('stopwords')

Getting Started
---------------

The first thing you'll want to do is create a `Search` instance, which allow you to pass a `key`, used for namespacing within Redis so that you may have several searches in the same db.
 
.. code-block:: pycon

    >>> import pyreds
    >>> search = pyreds.create_search('pets')

pyreds acts against arbitrary numeric or string based ids, so you could utilize this library with essentially anything you wish, even combining data stores. The following example just uses a list for our "database", containing some strings, which we add to pyreds by calling `Search#index()` padding the body of text and an id of some kind, in this case the index.

.. code-block:: pycon

    >>> strs = []
    >>> strs.append('Tobi wants four dollars')
    >>> strs.append('Tobi only wants $4')
    >>> strs.append('Loki is really fat')
    >>> strs.append('Loki, Jane, and Tobi are ferrets')
    >>> strs.append('Manny is a cat')
    >>> strs.append('Luna is a cat')
    >>> strs.append('Mustachio is a cat')
    >>> for i, v in enumerate(strs):
    ...     search.index(v, i)

To perform a query against pyreds simply invoke `Search#query()` with a string, which return a `Query` instance. Then invoke `Query#end()`, which return a list of ids when present, or an empty list otherwise.

.. code-block:: pycon

    >>> ids = search.query('Tobi dollars').end()
    >>> print('Search results for "Tobi dollars"'))
    >>> for id in ids:
    ...     print('  - {}'.format(strs[id]))

By default pyreds performs an intersection of the search words. The previous example would yield the following output since only one string contains both "Tobi" and "dollars":

.. code-block:: pycon

    Search results for "Tobi dollars":
        - Tobi wants four dollars

We can tweak pyreds to perform a union by passing either "union" or "or" to `Search#type()` between `Search#query()` and `Query#end()`, indicating that any of the constants computed may be present for the id to match.

.. code-block:: pycon

    >>> ids = search.query('tobi dollars').type('or').end()
    >>> print('Search results for "Tobi dollars"'))
    >>> for id in ids:
    ...     print('  - {}'.format(strs[id]))

The union search would yield the following since three strings contain either "Tobi" or "dollars":

.. code-block:: pycon

    Search results for "tobi dollars":
        - Tobi wants four dollars
        - Tobi only wants $4
        - Loki, Jane, and Tobi are ferrets

API
---

.. code-block:: pycon

    >>> search = pyreds.create_search(key)
    >>> search.index(text, id)
    >>> search.remove(id)
    >>> query = search.query(text[, type]) # will return a `Query` instance
    >>>
    >>> query.between(start, stop)
    >>> query.type(type)
    >>> query.end()

LICENSE
-------

The MIT License
