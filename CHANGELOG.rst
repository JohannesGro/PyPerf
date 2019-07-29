History
=======
0.4.1
-----
* Fix:
  RuntimeError occured when collecting the DBMS of cdb, when not DBMS is specified.
  https://git.contact.de/SD/pyperf/merge_requests/24

0.4.0
-----
* Improvement:
  Rework the user documentation
  https://git.contact.de/SD/pyperf/issues/35

* Improvement:
  Now using a Release Pipeline
  https://git.contact.de/SD/pyperf/issues/34

* Fix:
  Reworked the logging
  https://git.contact.de/SD/pyperf/issues/8

* Fix:
  Install dependencies fixed
  https://git.contact.de/SD/pyperf/merge_requests/18

* Feature dropped:
  Renderer is not part of PyPerf anymore
  https://git.contact.de/SD/pyperf/issues/23

* Fix:
  The DBMS is now part of the collected metadata
  https://git.contact.de/SD/pyperf/issues/15

* Improvement:
  Code coverage raised
  https://git.contact.de/SD/pyperf/issues/24

* Improvement:
  Python 3 combatibility ensured
  https://git.contact.de/SD/pyperf/issues/29

* Fix:
  Upload cancels if one benchmark doenst have results
  https://git.contact.de/SD/pyperf/issues/30

0.3.11
------
* Fix:
  The exceptions are now Python3 compatible.


0.3.10
------
* Improvement:
  The upload functionality should be more robust against InfluxDB outages
  https://git.contact.de/SD/pyperf/issues/27


0.3.9
-----
* Improvement:
  Provide an easy method for calling from a debugger/IDE
  https://de-git01.contact.de/SD/pyperf/issues/19

* Fix:
  'bench upload' throws a ZeroDevision exception when uploading a report with zero measurements
  https://de-git01.contact.de/SD/pyperf/issues/6

* Fix:
  PyPerf's dependencies should be installed automatically
  https://de-git01.contact.de/SD/pyperf/issues/17

* Improvement:
  Provide wheels to enable installing via pip


0.3.8
-----
* Improvement:
  Port to Py3
  https://de-git01.contact.de/SD/pyperf/issues/2

0.3.7
-----
* Improvement:
  Include docs in distribution
  https://de-git01.contact.de/SD/pyperf/issues/1

* Fix:
  'bench upload' uploads results from other benches

0.3.6
-----
* Improvement:
  Better names for the CLI
  https://de-git01.contact.de/SD/pyperf/issues/4

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
