Benchsuite
**********
The following figure displays an example of a benchsuite.json.

.. include:: example_benchsuite.json
   :literal:

A benchsuite has a simple structure. The root element is the *suite*. The *suite*
contains one or more benchmarks.

Each benchmark has three mandatory attributes.

:file: The *file* which contains the benchmark. This file could be a absolute path.
:className: Name of the benchmark class in the file.
:args: *args* includes a dict to configure the benchmark. The arguments listed here can be used within the bench (*self.args*).
