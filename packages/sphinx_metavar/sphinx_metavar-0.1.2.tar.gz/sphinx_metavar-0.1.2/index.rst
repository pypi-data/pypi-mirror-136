sphinx-metavar
==============

This is a simple extension to Sphinx_ that adds a missing piece of
semantic markup, namely metasyntactic variables.  It defines a
``:metavar:`` role, and patches the ``:samp:`` role so that it uses the
same styling for those parts within braces.  In HTML, metasyntactic
variables are marked up with italics, just as if you were using
emphasis, except that the ``<em>`` tag has the ``metavar`` class, so you
can override the style in CSS.  In plain text, metasyntactic variables
are uppercased.  Texinfo output uses the ``@var{}`` command, which
results in italics for HTML and PDF, and uppercase in Info [#]_.  In
other formats, metasyntactic variables are (currently) output the same
as emphasis.

Example usage:

.. code-block:: restructuredtext

  Bazing the foo requires a special command, used like:

  .. parsed-literal::

     \\Frobnicate \\for :metavar:`xyz`

  where :metavar:`xyz` is your spam of eggs.  If you do not need the eggs,
  you can use the simpler form :samp:`\\Frobnicate {xyz}`.


Output:

  Bazing the foo requires a special command, used like:

  .. parsed-literal::

     \\Frobnicate \\for :metavar:`xyz`

  where :metavar:`xyz` is your spam of eggs.  If you do not need the eggs,
  you can use the simpler form :samp:`\\Frobnicate {xyz}`.

Observe how the HTML version of this text uses custom CSS styling that
underlines metasyntactic variables.  This is done by adding a
:file:`metavar.css` file (using ``html_css_files = ['metavar.css']`` in
:file:`conf.py`) which contains:

.. code-block:: css

   .metavar {
     text-decoration: underline;
   }

.. _Sphinx: https://www.sphinx-doc.org

.. [#] Outputting ``@var{}`` for metasyntactic variables inside
       ``:samp:`` is done by Sphinx itself and this requires version
       4.4.
