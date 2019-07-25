.. _`tut_benchsuite`:

===================
Create a Benchsuite
===================

In this chapter you will learn how to create a Benchsuite out of the Benchclass in `database_bench.py`,
that we created in the previous chapter.

We start by creating a new file called `benchsuite.json`.
Every PyPerf Benchsuite contains a dictionary with the key :code:`"suite"`.

.. literalinclude:: ../examples/benchsuite_simple.json
    :language: json
    :lines: 1,2,8,9

This :code:`suite` again contains a dictionary.
This dictionary now contains all Benchmark we want to have in our Benchsuite.
So, we add another key to it. Let's call it :code:`DatabaseBench`. The value will be a dictionary as well.

.. literalinclude:: ../examples/benchsuite_simple.json
    :language: json
    :lines: 1,2,3,7,8,9

Inside the now created dictionary for our Bench, we have four mandatory fields.
These are :code:`"file"`, :code:`"className"`, :code:`"active"` and :code:`"args"`.

:code:`"file"` contains a string with the path to the file (relative to the benchsuite) containing
the Benchclass we want to execute.
So supposing `benchsuite.json` and `database_bench.py` are in the same directory, the path is just the
filename.

:code:`"className"` contains the name of the Python class inside the specified file. In our case that
will be :code:`DatabaseBench`.

:code:`"args"` contains a dictionary with arguments, that we can pass to our Benchclass. Since we do not
need any, this dictionary may be empty.

All this together results in the following Benchsuite:

.. literalinclude:: ../examples/benchsuite_simple.json
    :language: json

This Benchsuite is ready to be executed. In the next chapter :ref:`tut_firstrun` you will see, how this is done.