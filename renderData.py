#!c:\csall\trunk\sqlite\bin\powerscript.exe
import argparse
import json
import logging
import sys


logger = logging.getLogger("[" + __name__ + " - Renderer]")

benchmark_file = "benchmarkResults.json"
output_file = "benchmarkResults.html"

template = """
<html>
<head>
    <link rel="stylesheet" href="main.css">
</head>
<body>
<h1>Benchmark Results</h1>
{0}

</body>
</html>
"""


def main():
    data = loadJSONData()
    iterateBenches(data)


def iterateBenches(data):
    body = ""
    for bench_key, bench_val in data["results"].iteritems():
        logger.info("Render bench: " + bench_key)
        body += render_bench(bench_key, bench_val)

        # result = start_bench_script(bench_val["file"], bench_val["className"], bench_val["args"])
        # results['results'][bench_key] = {'args': bench_val["args"], 'data': result}
    writeHTML(template.format(body))


def render_bench(name, content):
    title = "<h2>{0}</h2>".format(name)
    args = render_args(content["args"])
    data = render_data(content["data"])
    return title + args + data
    # print args


def render_data(data):
    title_templ = "<h3>{0}</h3>"
    res = ""
    for d in data:
        for meth_name, content in d.iteritems():
            title = title_templ.format(meth_name)
            if isinstance(content, list):
                for ele in content:
                    body = render_types(ele)
            else:
                body = render_types(content)
            res = res + title + body
    return res


def render_types(content):
    res = "<h4>{}</h4>".format(content["type"])
    dl_temp = """
        <dl>
        {0}
       </dl>
    """
    dl_inner_temp = "<dt>{0}</dt><dd>{1}</dd>"
    if content["type"] == "time series":
        time_list = content["time"]["val"]
        len_time_list = len(time_list)
        if len_time_list > 0:
            max_val = max(time_list)
            min_val = min(time_list)
            sum_val = sum(time_list)
            avg_val = sum_val / len(time_list)
            dl_inner = ""
            dl_inner += dl_inner_temp.format("Unit:", content["time"]["unit"])
            dl_inner += dl_inner_temp.format("Max:", max_val)
            dl_inner += dl_inner_temp.format("Min:", min_val)
            dl_inner += dl_inner_temp.format("Sum:", sum_val)
            dl_inner += dl_inner_temp.format("Average:", avg_val)
            res += dl_temp.format(dl_inner)
    if content["type"] == "time":
        dl_inner = ""
        dl_inner += dl_inner_temp.format("Unit:", content["time"]["unit"])
        dl_inner += dl_inner_temp.format("Val:", content["time"]["val"])
        res += dl_temp.format(dl_inner)
    return res


def render_args(args):
    result = """
        <table>
            <tr>
                <th>Argument</th>
                <th>Value</th>
            </tr>
            {0}
        </table>
    """
    rows = ""
    for key, val in args.iteritems():
        rows = rows + "\n<tr><td>{0}</td><td>{1}</td></tr>".format(key, val)
    result = result.format(rows)
    return result


def loadJSONData():
    """
    This functions load the json-data.
    """
    try:
        with open(benchmark_file) as data_file:
            data = json.load(data_file)
    except IOError as err:
        logger.error("Could not open benchmark data file! " + str(err))
        sys.exit(1)
    except ValueError as err:  # JSONDecodeError inherrits from ValueError
        logger.error("Could not decode benchmark data file! " + str(err))
        sys.exit(1)
    except:
        logger.error("Unexpected error occurred! " + str(sys.exc_info()[:]))
        sys.exit(1)
    else:
        logger.info("Reading successful")
    return data


def writeHTML(data):
    """
    This functions dumps json data into a file.
    """
    logger.info("Saving Results to file: " + output_file)
    try:
        with open(output_file, 'w') as out:
            out.write(data)
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

if __name__ == "__main__":
    # CLI
    parser = argparse.ArgumentParser(description="""reads data of benchmarks from a json file.
                                    Each benchmakrs will be called rendered. Produces a html file with the results.""")
    parser.add_argument("--benchmarks", "-s", nargs=1, default=benchmark_file, help="A json file which contains the benchmarks.")
    parser.add_argument("--outfile", "-o", nargs=1, default=output_file, help="The results will be stored in this file.")

    # Grab the opts from argv
    opts = parser.parse_args()
    main()
