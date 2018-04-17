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


0.3.5
-----
* Improvement:
  Passing additional tags to "pyperf upload"
  https://de-git01.contact.de/SD/pyperf/issues/3

0.3.4
-----
* Fix:
  Fix the InfluxDB upload URL

0.3.3
-----
* Fix:
  Fix a time conversion bug when uploading to InfluxDB

0.3.2
-----
* Fix:
  Improve error handling and setting of exit code

* Improvement:
  Evaluate the 'active' configuration property

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
