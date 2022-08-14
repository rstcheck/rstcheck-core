FAQ / Known limitations / Known issues
======================================

Known limitations
-----------------

There are inherent limitations to what ``rstcheck-core`` can and cannot do. The reason for this is
that ``rstcheck-core`` itself relies on external tools for parsing and error reporting.
The rst source e.g. is given to ``docutils`` which then parses it and returns the errors.
Therefore ``rstcheck-core`` is more like an error accumulation tool. The same goes for the source
code in supported code blocks.

Known issues
------------

Code blocks without language (Sphinx)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

According to the `documentation for reStructuredText`_ over at docutils the language is an optional
argument to a code block directive.
In vanilla mode language-less code blocks are treated like code blocks which specified a language
that is not supported by ``rstcheck``.

When sphinx support is active however, a deeply nested issue arises in form of an
:py:exc:`AttributeError`. This exception has the unpleasant side-effect that linting for the whole
file containing this language-less code block fails. This may result in a false negative for
the file.

**There are currently only one fix available:**

Explicitly specifying the language for the code block.
This renders the ``highlight`` directive useless, but is the only known way to fix this issue.
And it enables checks of the source code inside those code blocks, if the language is supported of
cause.

This issue is tracked in issue :issue:`3`.


.. _documentation for reStructuredText: https://docutils.sourceforge.io/docs/ref/rst/directives.html#code
