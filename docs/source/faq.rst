FAQ / Known limitations
=======================

There are inherent limitations to what ``rstcheck-core`` can and cannot do. The reason for this is
that ``rstcheck-core`` itself relies on external tools for parsing and error reporting.
The rst source e.g. is given to ``docutils`` which then parses it and returns the errors.
Therefore ``rstcheck-core`` is more like an error accumulation tool. The same goes for the source
code in supported code blocks.
