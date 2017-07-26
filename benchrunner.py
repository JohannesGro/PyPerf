#!c:\ce\trunk\sqlite\bin\powerscript.exe
import importlib
import json
import logging.config
import sys

# bad practice?
suite_file = 'benchsuite.json'
output_file = 'benchmarkResults.json'
loggingConfigFile = 'loggingConf.json'


def main():
    logger.info("[Benchrunner]: Starting")
    logger.info("[Benchrunner]: Reading the benchsuite: " + suite_file)
    data = loadJSONData()
    results = {'results': {}}
    # iterating the suite
    for bench_key, bench_val in data["suite"].iteritems():
        if "active" in bench_val and (bench_val["active"] is False):
            continue
        logger.info("[Benchrunner]: Execute bench: " + bench_key)
        result = start_bench_script(bench_val["file"], bench_val["className"], bench_val["args"])
        results['results'][bench_key] = {'args': bench_val["args"], 'data': result}
    saveJSONData(results)


def loadJSONData():
    """
    This functions load the json-data.
    """
    try:
        with open(suite_file) as data_file:
            data = json.load(data_file)
    except IOError as err:
        logger.error("[Benchrunner]: Could not open benchsuite! " + str(err))
        sys.exit(1)
    except ValueError as err:  # JSONDecodeError inherrits from ValueError
        logger.error("[Benchrunner]: Could not decode benchsuite! " + str(err))
        sys.exit(1)
    except:
        logger.error("[Benchrunner]: Unexpected error occurred! " + str(sys.exc_info()[0:1]))
        sys.exit(1)
    else:
        logger.info("[Benchrunner]: Reading successful")
    return data


def saveJSONData(data):
    """
    This functions dumps json data into a file.
    """
    logger.info("[Benchrunner]: Saving Results to file: " + output_file)
    try:
        with open(output_file, 'w') as outfile:
            json.dump(data, outfile, sort_keys=True, indent=4)
    except IOError as err:
        logger.error("[Benchrunner]: Could not open file to save the data! " + str(err))
    except ValueError as err:  # JSONDecodeError inherrits from ValueError
        logger.error("[Benchrunner]: Could not decode values! " + str(err))
    except TypeError as err:
        logger.error("[Benchrunner]: Could not serialize object! " + str(err))
    except:
        logger.error("[Benchrunner]: Unexpected error occurred! " + str(sys.exc_info()[0:1]))
    else:
        logger.info("[Benchrunner]: Saving successful")


def start_bench_script(path, className, args):
    """ This functions imports the bench module and creates an instance of the given
    className. It calls the method .main(args) which is the entry point for
    the test classes."""
    try:
        mod = __import__(path, fromlist=[className])
        bench_class = getattr(mod, className)
    except ImportError as err:
        logger.error("[Benchrunner]: Could not import bench file! " + str(err))
        return
    except AttributeError as err:
        logger.error("[Benchrunner]: Could not find className: {0}! {1}".format(className, str(err)))
        return
    except:
        logger.error("[Benchrunner]: Unexpected error occurred! " + str(sys.exc_info()[0:1]))
        return

    # perform the benchmark
    return bench_class().run(args)


if __name__ == "__main__":
    # initialize the logging
    logging.basicConfig()
    with open(loggingConfigFile, "r") as configFile:
        logging.config.dictConfig(json.load(configFile))
    logger = logging.getLogger(__name__)
    main()
