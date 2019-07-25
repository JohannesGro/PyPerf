.. _`tut_bench`:

===================
Create a Benchclass
===================

In this chapter you will learn how to create a simple Benchclass, that will measure the duration of an
insert to a database with a fictional database module.

We start by creating a new file called `database_bench.py`.

PyPerf offers an abstract class called :code:`Bench` for our purpose of creating a Benchclass.
To use this we have to import this module and create a subclass of :code:`Bench`.

You will also want to import the :code:`Timer`, so that we can measure the elapsed time.

We also want to import the fictional database module, since we want to measure an insert of it.

.. literalinclude:: ../examples/database_bench_simple.py
    :language: python
    :lines: 1-7

Now we have a Benchclass that does nothing. To make this class to measure something,
it needs a function that may be called by PyPerf.

Such functions are always named with the prefix :emphasis:`bench_`.
Since we want to measure the duration of an insert we call this function :code:`bench_insert`.

Do not forget the :code:`self` parameter, since all bench functions have to be member functions of your
Benchclass.

.. literalinclude:: ../examples/database_bench_simple.py
    :language: python
    :lines: 7,8

Now we have prepared our class so that we can start to implement our bench function.

First we have to prepare everything for our test.
Therefore we connect to the database and create a table.
Additionally we create a list where we can store our results.

.. literalinclude:: ../examples/database_bench_simple.py
    :language: python
    :lines: 9-12
    :dedent: 8

Then we create the :code:`Timer` and the code we want to measure.

PyPerf's :code:`Timer` is a context manager. This means that you can create it
using a :code:`with` statement.

The :code:`Timer` will start measuring as soon as it enters the context and will stop as
soon as you leave the context of the :code:`Timer`.
So all statements that are in the context of the :code:`Timer` will be the statements that get measured.

Since we want to measure an insert into out database we will add this statement to the
:code:`Timer`'s context.

Also we put the Timer's result into our List we created before.

.. literalinclude:: ../examples/database_bench_simple.py
    :language: python
    :lines: 14-16
    :dedent: 12

Now our :code:`DatabaseBench` class is able to measure the duration of one insert statement.

To enable PyPerf to use this result for its output, we need to call the method :code:`storeResult`.

.. literalinclude:: ../examples/database_bench_simple.py
    :language: python
    :lines: 17
    :dedent: 8

This will store the elapsed seconds of our :code:`Timer` to :emphasis:`bench_sleep_duration` as a
:emphasis:`time_series`.

Since we don't just want to do the measuring only one time, we can do the measuring in a loop.

Now, when measuring our insert statement 10 times, our class looks like this:

.. literalinclude:: ../examples/database_bench_simple.py
    :language: python

And now we are done. We have created our first :code:`Bench` class.

In the next chapter you will learn, how to :ref:`tut_benchsuite`, so that PyPerf can run this Benchclass.
