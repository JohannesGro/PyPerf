.. _`howto_logging`:

==============
HowTo: Logging
==============

This chapter is all about logging. How it is configured and how this configuration can be
modified.

.. contents::
    :local:
    :backlinks: none

Logging
=======
The logging that PyPerf uses is the standard logging mechanism of python. It is used by importing
the logging module und creating a logger.

.. code-block:: python

    import logging

    logger = logging.getLogger(__name__)

Typically every module gets it's own logger, so the name given to the :code:`getLogger` method is
:code:`__name__`. This is usually done at top level of a module.
When doing your own logging it is advised to do so too, but of course you can name your logger as
you like, and also define it where you like.

When logging you have the posibillity to have different levels of logging. They are structured
hierarchically from lowest to highest like so:

    * DEBUG
    * INFO
    * WARNING
    * ERROR
    * CRITICAL


Standard Configuration
======================
The standard configuration for logging is based on the following `loggingConf.json`-file, that
pyperf uses to initialize the logging:

.. literalinclude:: ../../pyperf/log/loggingConf.json
    :language: json

This configuration file is a JSON format, that can be interpreted by PyPerf.
It is designed so that different logging-sources can be directed to different (or same) locations.

The different sources are :emphasis:`pyperf`, :emphasis:`benchmark` and :emphasis:`third-party`.

For every source there are three different types of location they can direct the logging to. These are
:emphasis:`stdout`, :emphasis:`stderr` and :emphasis:`files`.
For every location it is possible to set a minimum and a maximum for the loglevel.

By default, every log that :emphasis:`pyperf` creates itself will be displayed on
:emphasis:`stdout`, when the level is between :emphasis:`DEBUG` and :emphasis:`INFO`.
And every log whose level is between :emphasis:`WARNING` and :emphasis:`CRITICAL` will be
displayed on :emphasis:`stderr`.

Logs coming from :emphasis:`Benchmarks` behave the same regarding to :emphasis:`stdout` and
:emphasis:`stderr`, but will also write their logs to a file called :emphasis:`benchmark.log`, when the
loglevel is between :emphasis:`DEBUG` and :emphasis:`CRITICAL`.

Every other logging source that uses :emphasis:`Python's` logging mechanism will also write it's logs
to the :emphasis:`benchmark.log` file, when the loglevel is between :emphasis:`DEBUG` and
:emphasis:`CRITICAL`.

.. note::

    Logs with the loglevel :emphasis:`DEBUG` will only show up, when running PyPerf with the
    :emphasis:`-d` or :emphasis:`--debug` flag.


How to make your own configuration
==================================
You can also provide your own configuration file. It has to follow the following format:

.. code-block:: json

    {
      "SOURCE": {
        "stdout": {
          "min": "LOGLEVEL",
          "max": "LOGLEVEL"
        },
        "stderr": {
          "min": "LOGLEVEL",
          "max": "LOGLEVEL"
        },
        "file": {
          "filename": "FILENAME",
          "min": "LOGLEVEL",
          "max": "LOGLEVEL"
        }
      }
    }

You can replace :emphasis:`SOURCE` with either pyperf, benchmark or third-party, :emphasis:`LOGLEVEL`
with the loglevels mentioned above and :emphasis:`FILENAME` with a relative path to a file. Note, that
when specifying a path, all directories of the path have to exist.

In your configuration you can have up to three of these :emphasis:`SOURCE` blocks.
Every :emphasis:`SOURCE` block may have zero or one :emphasis:`stdout` blocks, zero or one
:emphasis:`stderr` blocks and as many :emphasis:`file` blocks as you want.

When not defining a :emphasis:`"min"`, the lowest loglevel that gets directed to your destination will
be :emphasis:`DEBUG`. Similar to that, not defining :emphasis:`"max"` results in having the maximum
loglevel set to :emphasis:`CRITICAL`.

When you want to use your own configuration file, remember to run pyperf by using the :emphasis:`-l` or
:emphasis:`--logconfig` flag, followed by your configuration file.
