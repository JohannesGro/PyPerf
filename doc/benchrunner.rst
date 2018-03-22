BenchRunner
***********

.. automodule:: pyperf.benchrunner
	:members:

	Members
	=======================


CLI
======================
In the following the command line interface will be shown.

.. code-block:: none

	usage: benchmark runner [-h] [--suite [SUITE]] [--outfile [OUTFILE]]
                        [--logconfig [LOGCONFIG]]

    The benchrunner runs different benchmarks. These benchmarks inherit from the
    abstract class 'Bench'. Several different benches can be collected and define
    by a benchsuite. A benchsuite describes a list of benches and their call
    parameter. The suite is stored in json format (Read more: :doc:`benchsuite`).
    The benchrunner reads the benchsuite and executes each bench. The benches
    return measurements which will be gathered and stored by the benchrunner. The
    result is stored in a json formatted outputfile.

    optional arguments:
      -h, --help            show this help message and exit
      --suite [SUITE], -s [SUITE]
                            A json file which contains the benches. (default:
                            benchsuite.json)
      --outfile [OUTFILE], -o [OUTFILE]
                            The results will be stored in this file. (default:
                            benchmarkResults_2017-10-05_12-56-12.json)
      --logconfig [LOGCONFIG], -l [LOGCONFIG]
                            Configuration file for the logger. (default:
                            benchrunner.log)
