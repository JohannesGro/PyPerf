Benchsuite
**********
In the following figure you can the see benchsuite file.

.. include:: example_benchsuite.json
   :literal:

A benchsuite has a simple structure. The root element is the *suite*. The *suite*
contains serveral benchmarks.

Each benchmark has three attribute.

:file: The *file* which contains the benchmark. This file could be a absolute path.
:className: Name of the benchmark class in the file.
:args: *args* includes a dict to configure the benchmark. The arguments listed here can be used within the bench (*self.args*). 
