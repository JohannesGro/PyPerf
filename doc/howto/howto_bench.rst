.. _`howto_bench`:

============
HowTo: Bench
============

The Benchclass we created in :ref:`tut_bench` was just the beginning of what a Benchclass can look like.
You will learn about all the features a Benchclass may have.

.. contents::
    :local:
    :backlinks: none


Typical Benchclass
==================

A typical Benchclass, that measures how long it takes to insert something into a database, could look
like this:

.. literalinclude:: ../examples/database_bench.py
    :language: python

Let's break it down.


Logging
-------
PyPerf offers the standard Python logging. So if you want to enable it, you need to get a logger.
To do this, you simply import the logging module and create a logger.

You should, since it is a python convention, always get your logger like this, so that all loggernames
are similar. Also note, that the default logging mechanism of PyPerf is based on this convention. So
if you don't follow it, your logging output may be strange.

For more input about PyPerf's logging mechanism, have a look at :ref:`howto_logging`.


:code:`bench_`-methods
----------------------
Methods like this, prefixed with `bench_` have a special meaning in PyPerf, since those are the methods
doing the actual measuring.

What you usually do in `bench_`-methods is:

    * create a list for what you measured
    * loop
        * create the Timer as context manager
            * do what you want to measure
        * put elapsed time in your list
    * store the list

The :code:`bench_insert` method is a nice example, showing how this pattern looks like in code.

Your Benchclass may have as many as methods like this as you want.


:code:`setUpClass` and :code:`tearDownClass`
--------------------------------------------
These two are special methods that are inherited from the parent class :code:`pyperf.Bench`.
Since :code:`pyperf.Bench` does not implement them, you don't have to implement those methods.
But doing so gives you a powerful feature, since these two methods get executed by PyPerf itself.

The intent of the :code:`setUpClass` method is to prepare everything that this class needs to be
prepared to run smoothly.

Similar to this, the :code:`tearDownClass` method is used to clean up after everything is done.

In the code example above you can see how this can be utilised.

As you can see, the :code:`setUpClass` method is establishing a connection to a database
and the :code:`tearDownClass` method is disconnecting the connection.

We recommend you, to make use of these methods, since it will improve the readability of your
Benchclass a lot.


:code:`setUp` and :code:`tearDown`
----------------------------------
These two methods are also inherited from :code:`pyperf.Bench` and work nearly the same.
The difference is, that these methods may be called more than once, depending on the number of
:code:`bench_`-methods.

The :code:`setUp` method is always executed right before any :code:`bench_`-method is executed and
the :code:`tearDown` method always right after any :code:`bench_`-method.

We also recommend using these two, since it will reduce the lenght of your :code:`bench_`-methods,
when they need the same prerequisites or cleaning up.


Helper methods
--------------
All methods that are not defined in the interface of :code:`pyperf.Bench` or not prefixed with
:code:`bench_` we call `helper methods`.

These methods do not have any special meaning in PyPerf, other than keeping your code clean and readable.
But we strongly recommend using helper methods, so that, for example, the code for the actual measuring
in :code:`bench_`-methods stays fairly small.

Also a good use of helper methods are :emphasis:`warmup`-methods. They can come in handy when
you expect your testresults to be effected by caching. In this case it would be advisable to
have such :emphasis:`warmup`-methods warming up the cache.

We also recommend prefixing those methods with an underscore to emphasize that these methods are just
for the internal use of your class, but it is not mandatory.

:code:`self.args`
-----------------
One last thing to mention is the :code:`args` dict of every Benchclass. This dict contains all
key-value pairs that are defined in the Benchsuite that runs your Benchclass. To see how this works,
have a look at :ref:`howto_benchsuite`.