.. _`tut_firstRun`:

=========================
Run PyPerf the first time
=========================

Now that we have a Benchclass and a Benchsuite it is time to execute PyPerf to run our Benchmark.
To do this, run the following command from the location of the `benchsuite.json`:

.. code-block:: console

    python -m pyperf run

This command will now start PyPerf and it will execute the Benchsuite.
On the console you should see something like

.. code-block:: console

    Logging enabled using configuration file /builds/SD/pyperf/pyperf/log/loggingConf.json
    Fetching system infos (verbose: False, CONTACT Elements available: False)
    Starting
    Reading the benchsuite 'benchsuite.json'
    Executing bench 'DatabaseBench'
    Results saved to benchmarkResults_2019-07-15_10-51-43.json

As you can see, the results of our Benchmark have been saved to a file called `benchmarkResults_%date%.json`:

Now, you can upload this benchmark result to your database, e.g. Influx, to store it. To do so, just execute
PyPerf with the subcommand :code:`upload` instead of :code:`run`, followed by the filename containing
the results. In our example this will result in the following command:

.. code-block:: console

    python -m pyperf upload benchmarkResults_2019-07-15_10-51-43.json

This will now upload the benchmark results to an `Influx Database` at `http://localhost:8086`.

Congratulations! You have finished the tutorial. For further reading you can have a look at:

* :ref:`usage` for
* :ref:`howto` for in depth details of PyPerf
* :ref:`reference` for PyPerf's API.