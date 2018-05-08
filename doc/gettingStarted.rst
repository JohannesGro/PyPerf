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


Renderer
========
The renderer creates a HTML file to display the results of the benchmarks.
There are two modes for the rendering. The default mode is comparison.
Benchmarks from several systems can be compared. A reference benchmark might be
specified to detect deviations. The `--trend` option is for showing trends in recurring
runs of the given benchmark.

E.g.:

.. code-block:: sh

	bench render [yourbenchmarks] --outfile out.html

The benchmarks value defines a list of benchmarks files. It also possible to pass
folders instead of a file. In this case the whole directory will be searched
for '.json' files.

The parameter `--outfile` or `-o` defines a name for the HTML file.

The renderer tries to display as much information as possible, that means
benchmarks will not be omitted if the benchmarks do not have the same benches or tests.

Read more: :doc:`renderer`

Compare
-------
As mentioned before there are two different modes for rendering the data.
The compare mode is used to compare benchmarks from several systems. It shows
tables with the results of each benchmarks. The type `time_series` is a list of
time measurements. These values can not be displayed as a list, they are therefore
accumulated (sum, average, max, min). A bar chart is drawn for each test within a
bench. For `time_series` the average value will be represented by the bars. This
mode is default.

Reference
+++++++++
The option `-r`or `--reference` can be used to define a reference file. This
benchmark is indicative for the comparison. The reference is used to mark outlier
or just values which distance to reference value exceed a certain limit.


Trend
-----
This mode is used to display a collection of benchmarks over a period of time.
The parameter `-t`or `-trend` has to be passed to start in this mode.
This mode does not display tables but trend charts. One of the three
(total, weekdays, 24h) time periods can be selected. When this mode is used
the reference option is ignored.


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
