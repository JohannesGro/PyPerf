.. _`howto_uploader`:

===============
HowTo: Uploader
===============
In this chapter you will learn how you can utilize the uploader the best for your needs.

In the tutorial :ref:`tut_firstRun` you already uploaded a benchmark result to an Influx database.
But there are several more features that help you getting those results and information into your
database.

.. contents::
    :local:
    :backlinks: none

Specifying a Database
=====================
When running the upload command of PyPerf the default Influx instance used is the one running at
:emphasis:`http://localhost:8086`.
Since it is, aside from testing reasons, not wise to use a local database, you can pass the URL
of your real Influx instance to PyPerf.

You do this with the :code:`--url` flag of the upload command, followed by the URL.

Also, in your Influx instance there may be various databases, that all contain different data.
PyPerf upload makes it possible to choose the database you want to upload your measurements to.
If you do not want to specify your own database, then PyPerf will use (or create if not existing) the
database :emphasis:`perf`.

You can to this by using the :code:`--db` flag of the upload command, followed by the name of the
database.

Specifying the set of system infos
==================================
When uploading your benchmark results usually a fixed set of system infos will be used as tags
in Influx.
These are:

    * :emphasis:`user`
    * :emphasis:`cpu_cores_logical` as :emphasis:`cpu_count`
    * :emphasis:`mem_total`
    * :emphasis:`os`
    * :emphasis:`vm`

If cdb can be imported, then these will also be added to the relevant sysinfos:

    * :emphasis:`ce_minor`
    * :emphasis:`ce_sl`
    * :emphasis:`dbms_driver`
    * :emphasis:`dbms_version`

When running the uploader with the :code:`--uploadconfig` followed by the filename of the config file
you can override this set of system infos and only those you specified in the config file will be used.

The file has to be a JSON file containing a dictionary, where every key corresponds to the system info
in your benchmark report file and every value corresponds to the name the tag will have in your
Influx DB.

For example, the content of the standard set with the additional system info :emphasis:`cpu` as the
influx tag :emphasis:`cpu_info` would look like this:

.. literalinclude:: ../examples/uploadconfig.json
    :language: json

Additional Information
======================
Sometimes the measured data and the system infos of a benchmark result are not enough and you want
your measurements to have more additional data in your database.
The uploader of PyPerf offers three way to achieve this.

Tags
----
By adding your own tags, you can achieve filtering your data better.
Imagine having the same system, but in different environments, e.g. a QA and a Production environment.

When running your Benchmarks in those two environments it may be, that the collected meta data in the
reports will be so similar, that you cannot differentiate between them. In that case you could
specify an additional tag containing the environment when uploading.

You could achieve this with the :code:`--tags <tag>:<value>` flag of the uploader.
This will create a new tag :code:`<tag>` for the measurement containing the :code:`<value>`.

The upload commands for the two different execution environments could then look like this:

.. code-block:: console

    python -m upload --tags environment:QA report_qa.json
    python -m upload --tags environment:Production report_production.json

.. note::
    Tags in an Influx database will always be represented as a string. So when you need the
    value being represented as something different, you should consider not adding it as
    a tag, but as a value.

    Also the variability of your tag values should not be too big, since tags in an Influx
    database are indexed. The greater the variability of your tags is, the greater the
    index of your Influx instance will be.

Values
------
Aside from tags, you could also add some more values to your measurement. Mostly this will be needed
when you have a data, that you would usually want to upload as a tag, but being represented as something
different than a string.

Then you can add :code:`--values <key>:<value>` to your upload command.

Timestamp
---------
The last way to add additional data to upload together with your measurement is the timestamp.
Usually the benchmark report contains the timestamp of when the benchmark was executed, but by
providing a timestamp you can override this value.

To do so, you simply add the :code:`--ts` flag of the uploader, followed by the timestamp and the
unit.

So for example, if you want to upload your measurement to the 01.01.2019 12:00h you could
call the uploader by using the following command:

.. code-block:: console

    python -m pyperf upload --ts 1546344000s report.json
