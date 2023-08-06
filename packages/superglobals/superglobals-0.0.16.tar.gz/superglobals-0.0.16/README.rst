Easy access to globals() from inside a python module.

See: https://stackoverflow.com/questions/15959534/visibility-of-global-variables-in-imported-modules/69029612#69029612

Using superglobals
==================

.. code-block:: python

    import superglobals
    
    from superglobals import *

    superglobals()[var] = value

    setglobal('test', 123)
    defaultglobal('test', 456)
    assert(getglobal('test') == 123)

    setglobal('a.b.c', 7)
    > a['b']['c'] == 7

    setglobal('a\.b\.c', 8)
    > globals()['a.b.c'] == 8


Changelog
=========

0.0.10: initial release (2021-09-02)
0.0.13: added dotted object heirachy expansion (2021-09-13)
