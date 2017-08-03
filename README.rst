HTML2Kirby
==========

|Build Status| |codecov|

This is a html to
`Kirbytext <https://getkirby.com/docs/content/text#links>`__ converter
for python.

It is currently in heavy development.

Installation
------------

HTML2Kirby is tested and suported from Python 3.4 upwards

TBD

Usage
-----

To use this package, simply import the package and feed it some html:

::

    from html2kirby import HTML2Kirby

    formatter = HTML2Kirby()
    formatter.feed("""<img src="https://placekitten.com/200/300" alt="kittens are cute" />""")

You can then access the result via ``.kirbytext`` attribute:

::

    print(formatter.kirbytext)
    # prints (image: https://placekitten.com/200/300 alt: kittesn are cute)

Testing
-------

Make sure you have Pytest installed (``pip install pytest``). Then just
invoke it:

::

    pytest

Supported Markup
----------------

As of now, following tags are supported:

-  Simple formatting (``<b>``, ``<strong>``, ``<i>``, ``<em>``)
-  Headings (``<h1>``, ``<h2>``, ...)
-  Images (``<img>``)
-  line breaks (``<br>``)
-  Paragraphs (``<p>``)
-  Blocks (``<pre>``, ``<code>``, ``<blockquote>``)
-  Links (``<a>``)
-  Horizontal rulers (``<hr>``)
-  Lists (``<ul>``, ``<ol>``, ``<li>``)

Passed markup
~~~~~~~~~~~~~

Markup tags that aren't implemented are just dropped except for
following tags:

-  table
-  tr
-  td
-  th
-  tbody
-  thead
-  strike
-  u
-  abbr
-  del

They will just be kept in the Kirbytext which should result in a valid
output.

Issues
------

In python3.4, the |unescape| doesn't quite convert all of the html 5
escaped characters such as – (en dash).

.. |Build Status| image:: https://travis-ci.org/liip/html2kirby.svg?branch=master
   :target: https://travis-ci.org/liip/html2kirby
.. |codecov| image:: https://codecov.io/gh/liip/html2kirby/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/liip/html2kirby
.. |unescape| image:: https://docs.python.org/3/library/html.html?highlight=html#html.unescape

