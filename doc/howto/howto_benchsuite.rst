.. _`howto_benchsuite`:

=================
HowTo: Benchsuite
=================

In this chapter you will learn how you can use benchsuites.

In the tutorial :ref:`tut_benchsuite` you have already seen how a simple benchsuite can be created.
But this example does not yet cover everything you can do with them.

As mentioned in the tutorial chapter, a benchsuite is a JSON object that has the following structure:

.. code-block:: json

    {
        "suite": {
        }
    }

Inside the suite may be zero or more Benchmarks that can be executed. Every Benchmark is a key denoting
the name of the Benchmark and a JSON dictionary as value, with the following structure:

.. code-block:: json

    {
        "Benchmark": {
            "file": "bench_source_file.py",
            "className": "Class_Name",
            "args": {}
        }
    }

Every Benchmark has the mandatory fields :code:`file`, :code:`className` and :code:`args`,
where args may be empty or contain a dictionary.

You can define the key :code:`active`, where the value is a boolean denotes, whether this Benchmark
shall be run by PyPerf or not, but if you do not have this key, the Benchmark will always be run.

So a Benchsuite may look like this:

.. literalinclude:: ../examples/benchsuite.json
    :language: json

You can see, that with a good benchsuite you can easily run the same Benchclass in different environments or
a different amount of times.

But of course you are not restricted in having Benchmarks using the same Benchclass, you can
define the Benchmarks in your Benchsuite as you like.
