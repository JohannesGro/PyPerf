Getting Started
*************************

Install
=======
In order to install the PyPerf, we are using the `setup.py`.
Just call the the `setup.py` with the `install` command, which installs everything
from the build directory.

.. code-block:: sh

	python setup.py install


Benchmarks
==========
After installing PyPerf the benchmarks may be created and run.
These benchmarks inherit from the abstract class 'Bench' (Read more: :doc:`bench`).
Benchmarks are similar to unit tests. They have methods like `setup`, `tearDown` etc.
If you want to learn how to create a benchmark, please read :doc:`howtoBenchmark`.


Benchsuite
==========
A benchsuite describes a number of benches and their call
parameters. The suite is stored in JSON format.
Add the created Benchmarks of the previous step to a benchsuite
(Read more: :doc:`benchsuite`).


Runner
======
The benchrunner runs different benchmarks. It reads the benchsuite and
executes each bench. The benches return measurements which will be gathered
and stored in a JSON formatted output file.

.. code-block:: sh

	bench run --suite suite.json --outfile out.json

The parameter `--suite` or `-s` specifies a benchsuite. Replace `suite.json` with your benchsuite.

The parameter `--outfile` or `-o` defines a name for the JSON/HTML file.
`date` is a placeholder for the current date.

Read more: :doc:`benchrunner`

Running using the API
---------------------
If running using the CLI doesn't suite your needs (i.e. you want to
debug just one module in the IDE), you may use the API. Herefore, call
:samp:`pyperf/Benchrunner.main()` saying it where to read the configuration
from and where to write the output to:

.. code-block:: Python

	from pyperf.benchrunner import Benchrunner
	Benchrunner().main("path_to_config.json", "report.json")


Upload
========
PyPerf is also able to upload the gathered data to an instance of InfluxDB in order
for the data to be then displayed in Grafana. The upload option takes a JSON-file
to upload.

.. code-block:: sh

	bench upload report.json --target=influx --db=[yourDBname] --url=[yourInfluxDBhost]

The optional parameter `--target` or `-t` specifies the target storage to upload to with
influx as default.

The optional parameter `--db` determines the name of your database (default: perf).

The optional parameter `--url` specifies the host on which your database runs
(default: http://localhost:8086).

`--ts` overrides the timestamp given in the report. Valid units are 's' and 'us'.

`--values`, adds additional values to upload.

`--tags`, adds additional tags to upload.
