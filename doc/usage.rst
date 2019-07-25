.. _`usage`:

==========
Usage
==========

.. contents::
    :local:
    :backlinks: none

CLI
===

pyperf run
----------

.. code-block:: console

    python -m pyperf run [-h] [-s [SUITE]] [-o [OUTFILE]] [-l [LOGCONFIG]] [-d] [-v]

Description
:::::::::::
PyPerf run is used for executing benchmarks. It reads a benchsuite and runs the Benches specified in
the benchsuite. The measurements the benches return will be stored in a JSON formatted output file.

Options
:::::::

-d, --debug
    Get some more logging.

    This parameter enables the DEBUG loglevel.

-h, --help
    Shows the help message and exit

-l <LOGCONFIG>, --logconfig <LOGCONFIG>
    Configuration file for the logger.

    The configuration file has to be a valid JSON file. For more information about the logconfig,
    visit :ref:`howto_logging`.

-o <OUTFILE>, --outfile <OUTFILE>
    The results will be stored in this file (default: benchmarkResults_YYYY-mm-dd_HH-MM-SS.json).

    This will write the report to the specified OUTFILE.

-s <SUITE>, --suite <SUITE>
    A JSON file which specifies how to run the benches (default: benchsuite.json).

    Used to specify a custom benchsuite. The specified benchsuite has follow the format described at
    :ref:`howto_benchsuite`.

-v, --verbose
    Get more detailled system infos.

    The report file that PyPerf will generate will have more detailed infos about the machine that
    runs PyPerf. For detailed information about this have a look at :ref:`ref_sysinfos`.

Examples
::::::::

Run a benchsuite
................

.. code-block:: console

    python -m pyperf run

will result in executing PyPerf running the Benches as specified in :emphasis:`benchsuite.json`.
The output will be :emphasis:`benchmarkResults_YYYY-mm-dd_HH-MM-SS.json`

Run a benchsuite with custom logging
....................................

.. code-block:: console

    python -m pyperf run -v -d -l custom_logconfig.json

does the same, but more system information will be collected and the logging will be as
specified in :emphasis:`custom_logconfig.json` with the DEBUG loglevel enabled.

Run a custom benchsuite and write to custom output-file
.......................................................
.. code-block:: console

    python -m pyperf run -s custom_benchsuite.json -o report.json

will result in executing PyPerf running the Benches as specified in :emphasis:`custom_benchsuite.json`.
The output will be :emphasis:`report.json`.

pyperf upload
-------------

.. code-block:: console

    python -m pyperf upload [-h] [-t TARGET] [--url URL] [--db DB]
                  [--ts <timestamp><unit>] [--values VALUES] [--tags TAGS]
                  filename


Description
:::::::::::
PyPerf upload is used for uploading a reportfile created by PyPerf run to an Influx Database.


Options
:::::::

-h, --help
    show this help message and exit

-t <TARGET>, --target <TARGET>
    The target storage to upload to (default: influx)

--db <DB>
    The database to upload the results into (default: perf)

--url <URL>
    The URL of the Influx DBMS to upload onto (default: http://localhost:8086)

--tags <TAGS>
    Additional tags to upload.

--ts <(timestamp)(unit)>
    If given, overrides the timestamp given in the report. Valid units are 's' and 'ms'.

--values <VALUES>
    Additional values to upload.

Examples
::::::::

Uploading a benchresult
.......................

.. code-block:: console

    python -m pyperf upload report.json

will upload the report file :emphasis:`report.json` to the :emphasis:`perf` database in your local
Influx instance.

Upload a benchresult to another influx instance
...............................................

.. code-block:: console

    python -m pyperf upload --url http://influxdb.customhost.com:8086 report.json

will upload the report file :emphasis:`report.json` to the :emphasis:`perf` database of the Influx
instance at :emphasis:`http://influxdb.customhost.com:8086`.

Upload with custom tags and timestamp
.....................................

.. code-block:: console

    python -m pyperf upload --tags newtag:yes --ts 1546344000s report.json

will upload the report file :emphasis:`report.json` to the :emphasis:`perf` database in your local
Influx instance. The measurement in the database will have the additional tag :emphasis:`newtag`
with the value :emphasis:`yes`. The measurement will also have it's time field set to
:emphasis:`1546344000s`, which is the 01-01-2019 12:00h.

API
===
If you do not want to run PyPerf by it's command line interface, you may use it's API.
Doing so enables you to embed PyPerf into your IDE for debugging.

Running Benchmarks
------------------
.. code-block:: python

    from pyperf.benchrunner import main
    Benchrunner().main("path_to_benchsuite.json", "output_file.json")

When using the API for running benchmarks you have to call the :code:`main` method of the
:code:`Benchrunner` class. The required parameters are the path to the benchsuite and the path for
the output file.

For a detailed information about this call, have a look at :ref:`ref_benchrunner`.

Uploading Benchmark Results
---------------------------
.. code-block:: python

    from pyperf.uploader import upload_2_influx
    upload_2_influx("report_file.json", "http://influx_url.com:8086", "database")

When using the API for uploading benchmark results you have to call the
:code:`upload_2_influx` function of the :code:`Uploader` module.
The required parameters are the path to the benchmark report, the URL of your Influx instance and
the database in you Influx instance to upload the data to.

For a detailed information about this call, have a look at :ref:`ref_uploader`.