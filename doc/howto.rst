How to create a benchmark
*************************
Each benchmark class has to derive from :doc:`bench`. :doc:`bench` provides several methods
and a interface for the :doc:`benchrunner`.

.. code-block:: py

  from benchmarktool.bench import Bench
  class SqliteBenchmark(Bench):

logging
=======
The benchrunner initializes the logger.
Import the *logging* module and call the *getLogger* function.

.. code-block:: py

  import logging
  logger = logging.getLogger("[" + __name__ + " - SqliteBenchmark]")

Tests
=======
A benchmark consists of several test. These tests a characterized by the prefix
\"bench\_\". The order of the execution is alphabetical. Methods without that prefix will
not be executed.

The *setUpClass* is called at the very beginning. And could be used for preparing
the benchmark. In this example_ it is used to establish a connection to a database.

The *tearDownClass* is called after the last test. And could be used for cleaning up
the benchmark. In this example_ it is used to close the connection to a database.

Before each test the *setUp* method is called to prepare the test fixture.
In this example_ it is used to create a new db table.

The Method *tearDown* is called immediately after the test method has been called. Usually this method
is used for cleaning purposes. In this example_ it is used to drop a table of the database.

There are serveral ways for creating the test. If you need to execute the tests in a specific order,
you could create bench methods in alphabetical order. Bench methods have the prefix 'bench_' and are called automatically. A other way is to create one bench
method to call several non bench methods. The *namespace* variable could be useful for this purpose.
The code below shows a bench ('bench_update') method calling a non bench method ('do_inserts'), which does a measurement. The namespace
is used to associate the call to *bench_update*. The measurements are store under the designation
`bench_update_do_inserts`.

.. code-block:: py

  from benchmarktool.timer import Timer
  def bench_update(self):
        self.namespace = "bench_update_"
        self.do_inserts(self.args['rows'])

Timer
=====
In order to measure the time the class *Timer* was introduced. The class can be used
with the *with* statement, because of its runtime context.

.. code-block:: py

  with Timer() as t:
    print "This action will be timed."
  print "Elapsed Time: %f" % t.elapsed.total_seconds()

*t.elapsed-total_seconds()* returns elapsed time.

Example
=======
The following example is a benchmark for a sqlite db.
It is not really practicable. It is supposed to show how a benchmark could look like.

.. include:: example_sqlite_benchmark.py
   :literal:
