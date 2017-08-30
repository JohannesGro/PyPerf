#!c:\ce\trunk\sqlite\bin\powerscript.exe
# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2017 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/
import argparse
import json
import logging
import os
import sys


logger = logging.getLogger("[" + __name__ + " - Renderer]")
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


current_path = os.path.abspath(os.path.dirname(__file__))
benchmark_file = os.path.join(current_path, "benchmarkResults.json")
output_file = os.path.join(current_path, "html", "benchmarkResults.html")

template = """
<html>
<head>
    <link rel="stylesheet" href="./assets/css/main.css">
    <link rel="stylesheet" href="./assets/css/barChart.css">
    <script src="./assets/js/d3.v4.min.js"></script>
    <script src="./assets/js/charts.js"></script>
</head>
<body>
<h1>Benchmark Results</h1>
{0}

</body>
</html>
"""
data = {}


def main():
    logger.debug("benchmarks files: {}".format(opts.benchmarks))
    logger.debug("output file: {}".format(opts.outfile))
    if isinstance(opts.benchmarks, list):
        renderMultipleBenchmarks()
    else:
        renderSingleBenchmark()
    iterateBenches(data)


def renderSingleBenchmark():
    data[opts.benchmarks] = loadJSONData(opts.benchmarks)


def renderMultipleBenchmarks():
    for fileName in opts.benchmarks:
        data[fileName] = loadJSONData(fileName)
    areBenchmarksComparable(data)


def areBenchmarksComparable(benchmarks):
    """Checks the structure of each benchmark result. The same benchsuite is
    necessary for comparison. The benches and the arguments are therefore checked."""

    b0 = benchmarks.values()[0]
    for bn in benchmarks.values():
        if b0["results"].keys() != bn["results"].keys():
            raise RuntimeError("Can not compare given benchmarks! Different benches.")
        for bench_key, bench_val in bn["results"].iteritems():
            if b0["results"][bench_key]["args"] != bn["results"][bench_key]["args"]:
                raise RuntimeError("Can not compare given benchmarks! Different args in bench: %s" % bench_key)


def iterateBenches(data):
    body = ""
    b0 = data.values()[0]
    for bench_key, bench_val in b0["results"].iteritems():
        logger.info("Render bench: " + bench_key)
        body += renderSingleBench(bench_key, bench_val)
    writeHTML(template.format(body), opts.outfile)


def renderSingleBench(bench_key, bench_val):
    title = "<h2>{0}</h2>".format(bench_key)
    tile_templ = "<div class='tile'>{0}</div>"
    args = renderBenchArgs(bench_val["args"])
    data = renderBenchData(bench_key, bench_val["data"])
    return tile_templ.format(title + args + data)
    # print args


def renderBenchData(bench_name, bench_val):
    title_templ = "<h3>{0}</h3>"
    content_templ = "<div class='content'>{0}</div>"
    res = ""
    body = ""
    if len(data) == 1:
        body = createDiagramm(bench_val)
    # for (bench_test, bench_test_content) in bench_val.iteritems():
        # title = title_templ.format(bench_test)
        # body = renderTextByType(bench_val)
        # res = res + tile_templ.format(title + body)
    body += renderTablesByTypes(bench_name, bench_val)
    # return content_templ.format(res)
    return body


def getTestResult(fileName, benchName, benchTest):
    return data[fileName]["results"][benchName]["data"][benchTest]


def createDiagramm(bench_val):
    elementTempl = """
    <div id="{0}">
        <script>
            var bench_val = {1};
            createBarChart("#{0}",bench_val);
        </script>
     </div>"""
    table_content = []
    for (bench_test_name, content) in bench_val.iteritems():
        val = content["value"]
        if content["type"] == "time_series":
            time_list = content["value"]
            sum_time = sum(time_list)
            avg = sum_time / len(time_list)
            val = avg

        table_content.append({"name": bench_test_name.encode('UTF-8'), "value": val})
    return elementTempl.format(bench_test_name, table_content)


def renderTableByType(bench_name, bench_val, type):
    header = "<h4>Tabelle {}</h4>".format(type)
    elements = dict((bench_test_name, content) for (bench_test_name, content) in bench_val.iteritems() if content["type"] == type)
    if len(elements) == 0:
        return ""

    content = "<table>"
    if type == "time_series":
        content += renderTimeSeriesRows(bench_name, elements)
    elif type == "time":
        content += renderTimeRows(bench_name, elements)

    content += "</table>"
    return header + content


def renderTimeRows(bench_name, elements):
    content = ""

    header_templ = "<tr>" + "<th>{}</th>" * (len(data) + 1) + "</tr>"
    row_templ = "<tr>" + "<td>{}</td>" * (len(data) + 1) + "</tr>"

    content += header_templ.format("Test", *data.keys())
    for benchTestName in elements.keys():
        res = []
        for fileName in data.keys():
            res.append(getTestResult(fileName, bench_name, benchTestName)["value"])
        content += row_templ.format(benchTestName, *res)
    return content


def renderTimeSeriesRows(bench_name, elements):
    content = ""

    header_templ = "<tr>" + "<th>{}</th>" * (len(data) + 2) + "</tr>"
    outer_row_templ = "<tr><td>{}</td><td colspan='{}'><table>{}</table></td></tr>"
    inner_row_templ = "<tr>" + "<td>{}</td>" * (len(data) + 1) + "</tr>"

    content += header_templ.format("Test", "Aggregation", *data.keys())
    for benchTestName in elements.keys():
        inner_content = ""
        res_max = []
        res_min = []
        res_sum = []
        res_avg = []
        for fileName in data.keys():
            time_list = getTestResult(fileName, bench_name, benchTestName)["value"]
            max_val = max(time_list)
            min_val = min(time_list)
            sum_val = sum(time_list)
            avg_val = sum_val / len(time_list)
            res_max.append(max_val)
            res_min.append(min_val)
            res_sum.append(sum_val)
            res_avg.append(avg_val)
        inner_content += inner_row_templ.format("Max", *res_max)
        inner_content += inner_row_templ.format("Min", *res_min)
        inner_content += inner_row_templ.format("Sum", *res_sum)
        inner_content += inner_row_templ.format("Average", *res_avg)
        content += outer_row_templ.format(benchTestName, (len(data) + 1), inner_content)

    return content


def renderTablesByTypes(bench_name, bench_val):
    types = ["time", "time_series"]
    res = ""
    for t in types:
        res += renderTableByType(bench_name, bench_val, t)
    return res


def renderTextByType(content):
    res = "<h4>{}</h4>".format(content["type"])
    dl_temp = """
        <dl>
        {0}
       </dl>
    """
    dl_inner_temp = "<dt>{0}</dt><dd>{1}</dd>"
    if content["type"] == "time_series":
        time_list = content["value"]
        len_time_list = len(time_list)
        if len_time_list > 0:
            max_val = max(time_list)
            min_val = min(time_list)
            sum_val = sum(time_list)
            avg_val = sum_val / len(time_list)
            dl_inner = ""
            dl_inner += dl_inner_temp.format("Unit:", content["unit"])
            dl_inner += dl_inner_temp.format("Max:", max_val)
            dl_inner += dl_inner_temp.format("Min:", min_val)
            dl_inner += dl_inner_temp.format("Sum:", sum_val)
            if "totalTime" in content:
                dl_inner += dl_inner_temp.format("Total Time:", content["totalTime"])
            dl_inner += dl_inner_temp.format("Average:", avg_val)
            res += dl_temp.format(dl_inner)
    if content["type"] == "time":
        dl_inner = ""
        dl_inner += dl_inner_temp.format("Result:", str(content["value"]) + " " + content["unit"])
        res += dl_temp.format(dl_inner)
    return res


def renderBenchArgs(args):
    """Displays the arguments in a table"""
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


def loadJSONData(file):
    """
    This functions load the json-data.
    """
    try:
        with open(file) as data_file:
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


def writeHTML(data, outfile):
    """
    This functions dumps json data into a file.
    """
    logger.info("Saving Results to file: " + outfile)
    try:
        with open(outfile, 'w') as out:
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
    parser.add_argument("--benchmarks", "-s", nargs='+', default=benchmark_file, help="One or more json files which contain the benchmarks.")
    parser.add_argument("--outfile", "-o", nargs=1, default=output_file, help="The results will be stored in this file.")

    # Grab the opts from argv
    opts = parser.parse_args()
    main()
