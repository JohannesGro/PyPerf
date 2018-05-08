How to create a benchmark
*************************
Each benchmark class has to derive from :doc:`bench`. :doc:`bench` provides several methods
and an interface for the :doc:`benchrunner`.

.. code-block:: py

  from pyperf.bench import Bench
  class OperationCreate(Bench):

logging
=======
The benchrunner initializes the logger.
Import the *logging* module and call the *getLogger* function.

.. code-block:: py

  import logging
  logger = logging.getLogger("[" + __name__ + " - OperationCreate]")

Tests
=======
A benchmark consists of several test. These tests are characterized by the prefix
\"bench\_\". The order of the execution is alphabetical. Methods without that prefix will
not be executed.

The *setUpClass* is called at the very beginning. It is used for preparing
the benchmark. In this example_ it is used to ensure all necessary services
are running and if not, they are started and the warmup method is called to
avoid a cold startup.

The *tearDownClass* is called after the last iteration and is usually used for
cleaning up after the benchmark. In this example_ it is used to delete all
created objects during the execution of the benchmark.

There are several ways for creating tests. If you need to execute the tests in a
specific order, you could create bench methods in alphabetical order. Bench methods
have the prefix \"bench\_\" and are called automatically. Another way is to create
one bench method to call several non bench methods. The *namespace* variable is
useful for this purpose.
The code below shows a bench ('bench_update') method calling a non bench method
('do_inserts'), which does a measurement. The namespace is used to associate the
call to *bench_update*. The measurements are store under the designation
`bench_update_do_inserts`.

.. code-block:: py

  from pyperf.timer import Timer
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
The following example is a benchmark for the operation create.
It is supposed to show how a simple benchmark looks like.

.. include:: example_operation_create.py
   :literal:
