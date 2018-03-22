Getting Started
*************************

Install
=======
In order to install the benchmark tool, we are using the `setup.py`.
Just call the the `setup.py` with the `install` command, which installs everthing from the build directory.

.. code-block:: sh

	python setup.py install


Benchmarks
==========
After installing the benchmark tool the benchmarks can be created.
These benchmarks inherit from the abstract class 'Bench' (Read more: :doc:`bench`).
Benchmarks are similar to unit test. They have methods like `setup`, `tearDown` etc.
If you want to learn how to create a benchmark, please read this text (:doc:`howtoBenchmark`).


Benchsuite
==========
A benchsuite describes a list of benches and their call
parameter. Several different benches can be collected and define
by a benchsuite. The suite is stored in json format.
Add the created Benchmarks of the previous step to a benchsuite (Read more: :doc:`benchsuite`).


Runner
======
The benchrunner runs different benchmarks. The benchrunner reads the benchsuite and executes each bench. The benches
return measurements which will be gathered and stored by the benchrunner. The
result is stored in a json formatted outputfile.

.. code-block:: sh

	c:\pyperf\benchmark.exe runner -s suite.json -o out.json

The parameter `-s` or `--suite` specifies a benchsuite. This is `benchsuite.json` by default. Replace `suite.json` with your benchsuite.

The paremeter `-o` or `--outfile` defines a name for the html file. This is `benchmarkResults_date.html` by default.
`date` is a placeholder for the current date.


Renderer
========
The renderer creates a html file to display the results of the benchmarks.
There are two modes for the rendering.
The first one is for comparison purpose.
Benchmarks from several systems can be compared. A reference benchmark could be specified to detect deviations.
The other one is for showing a trend. If you check the same system for a period of time.

E.g.:

.. code-block:: sh

	c:\pyperf\benchmark.exe render -b . -o out.html

The parameter `-b` or `--benchmarks` defines a list of benchmarks files. It also possible to pass folders instead of a file.
In this case the whole directory will be search for '.json' files. Files and folders could be mixed like this:
`-b . benchmarksfile.json myFolder`. This parameter is required.

The paremeter `-o` or `--outfile` defines a name for the html file. This is `benchmarkResults_date.html` by default.
`date` is a placeholder for the current date.

The renderer tries to display as much information as possbile, that means benchmarks will not be omitted if the benchmarks do not have the same benches or tests.


Compare
-------
As mentioned before there are two different modes for rendering the data.
This mode is used to compare benchmarks from several systems. It shows tables with the results of each benchmarks.
The type `time_series` is a list of time measurements. These values can not be shown as a list, they are therefore accumulated (sum, average, max, min).
A bar chart is drawn for each test within a bench. For `time_series` the average value will be represented by the bars. This mode is default.

Reference
+++++++++
The option `-r`or `--reference` can be used for define a reference file. This benchmark is indicative for the comparison.
The reference is used to mark outlier or just values which distance to reference value exceed a certain limit.


Trend
-----
This mode is used to display a collection of benchmarks for period of time. The parameter `-t`or `-trend` has to be passed to start in this mode.
This mode does not display tables but trend charts. One of three (total, weekdays, 24h) time periods can be selected. When this mode is used the reference option
is ignored.
