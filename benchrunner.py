#!launcher.cmd
import argparse
import importlib
import json
import logging.config
import sys

"""The benchrunner runs different benchmarks.
These benchmarks inherit from the abstract class Bench.
A benchsuit discribes a list of benchmarks and their parameters.
The runner reads the bensuit, calls the benches, gathers the results and creates a
 json formatted outputfile.
"""

# defaults
suite_file = 'benchsuite.json'
output_file = 'benchmarkResults.json'
loggingConfigFile = 'loggingConf.json'


def main():
    logger.info("Starting")
    logger.info("Reading the benchsuite: " + opts.suite)
    data = loadJSONData()
    results = {'results': {}}
    # iterating the suite
    for bench_key, bench_val in data["suite"].iteritems():
        if "active" in bench_val and (bench_val["active"] is False):
            continue
        logger.info("Execute bench: " + bench_key)
        result = start_bench_script(bench_val["file"], bench_val["className"], bench_val["args"])
        results['results'][bench_key] = {'args': bench_val["args"], 'data': result}
    saveJSONData(results)


def loadJSONData():
    """This functions load the json-data and returns it.
    """
    try:
        with open(opts.suite) as data_file:
            data = json.load(data_file)
    except IOError as err:
        logger.error("Could not open benchsuite! " + str(err))
        sys.exit(1)
    except ValueError as err:  # JSONDecodeError inherrits from ValueError
        logger.error("Could not decode benchsuite! " + str(err))
        sys.exit(1)
    except:
        logger.error("Unexpected error occurred! " + str(sys.exc_info()[0:1]))
        sys.exit(1)
    else:
        logger.info("Reading successful")
    return data


def saveJSONData(data):
    """This functions dumps json data into a file.
    """
    logger.info("Saving Results to file: " + opts.outfile)
    try:
        with open(opts.outfile, 'w') as outfile:
            json.dump(data, outfile, sort_keys=True, indent=4)
    except IOError as err:
        logger.error("Could not open file to save the data! " + str(err))
    except ValueError as err:  # JSONDecodeError inherrits from ValueError
        logger.error("Could not decode values! " + str(err))
    except TypeError as err:
        logger.error("Could not serialize object! " + str(err))
    except:
        logger.error("Unexpected error occurred! " + str(sys.exc_info()[0:1]))
    else:
        logger.info("Saving successful")


def start_bench_script(path, className, args):
    """This functions imports the bench module and creates an instance of the given
    className. It calls the method .main(args) which is the entry point for
    the test classes."""
    try:
        mod = __import__(path, fromlist=[className])
        bench_class = getattr(mod, className)
    except ImportError as err:
        logger.error("Could not import bench file! " + str(err))
        return
    except AttributeError as err:
        logger.error("Could not find className: {0}! {1}".format(className, str(err)))
        return
    except:
        logger.error("Unexpected error occurred! " + str(sys.exc_info()[0:1]))
        return

    # perform the benchmark
    return bench_class().run(args)


if __name__ == "__main__":
    # CLI
    parser = argparse.ArgumentParser(description="""The benchrunner reads benches from a benchsuite.
                                    Each bench will be called with an argument list. The result will
                                    be printet into outfile. The file format is json.""")
    parser.add_argument("--suite", "-s", nargs=1, default=suite_file, help="A json file which contains the benches.")
    parser.add_argument("--outfile", "-o", nargs=1, default=output_file, help="The results will be stored in this file.")
    parser.add_argument("--logconfig", "-l", nargs=1, default=loggingConfigFile, help="Configuration for the logger.")

    # Grab the opts from argv
    opts = parser.parse_args()

    # removing the root handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    # initialize the logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    # try to read config
    with open(opts.logconfig, "r") as configFile:
        logging.config.dictConfig(json.load(configFile))
        pass
    logger = logging.getLogger("[Benchrunner]")
    logger.debug("Options: " + str(opts))
    main()
