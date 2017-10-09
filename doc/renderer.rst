Renderer
***********

.. automodule:: benchmarktool.renderer
	:members:

	Members
	=======================

CLI
======================
In the following the command line interface will be shown.

.. code-block:: none

    usage: benchmark render [-h] [--benchmarks BENCHMARKS [BENCHMARKS ...]]
                            [--outfile [OUTFILE]] [--reference [REFERENCE]]
                            [--logconfig [LOGCONFIG]] [--trend]

    The class renderer reads the results of one or several benchmarks and creates
    a human readable output for example showing table or diagrams. The renderer
    provides two use cases. Firstly, a comparison between a plurality of
    benchmarks. Secondly, a analysis and determine a trend of a single system. A
    json file created by the benchrunner can be taken as a input. Currently this
    module supports html output only.

    optional arguments:
      -h, --help            show this help message and exit
      --benchmarks BENCHMARKS [BENCHMARKS ...], -b BENCHMARKS [BENCHMARKS ...]
                            One or more json files which contain the benchmarks.
                            It is also possible to use folders. All json files
                            from a folder will be loaded.
      --outfile [OUTFILE], -o [OUTFILE]
                            The results will be stored in this file (html).
      --reference [REFERENCE], -r [REFERENCE]
                            A referenced benchmark for the comparision. Uses the
                            reference to mark some benchmarks result as positiv or
                            negativ. This option will be ignored if the -trend
                            option is active.
      --logconfig [LOGCONFIG], -l [LOGCONFIG]
                            Configuration file for the logger.
      --trend, -t           Using the benchmarks to show a trend of a system.


