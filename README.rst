PyPerf
=======================

The PyPerf project aims to provide a base for writing standardized benchmarks.
For this purpose the project has two main parts. Firstly a runner executes the
benchmakrs and saves the result. Secondly a renderer reads the results and displays
it in a human readable manner.
It is possible to define a suite of benchmarks, run the suite on several systems
and compare the results or display a trend on a single system.

For more information have a look at our documentation.


History
=======

0.3.1
-----
* Fix:
  Pyperf should set the exit code in error cases appropriately

0.3.0
-----
* Improvement:
  Make callable as a module (python -m pyperf)

0.2
---
Initial release
