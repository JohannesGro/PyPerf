#!c:\ce\trunk\sqlite\bin\powerscript.exe
# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2017 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

"""The module renderer reads the results of one or several benchmarks and
create a human readable output for example showing table or diagramms.
A json file created by the benchrunner can be taken as a input. Currently this
module supports html output only.
"""

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


currentPath = os.path.abspath(os.path.dirname(__file__))
benchmarkFile = os.path.join(currentPath, "benchmarkResults.json")
outputFile = "benchmarkResults.html"

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
        loadDataForMultipleBenchmarks()
    else:
        loadDataForSingleBenchmark()
    iterateBenches()


def renderSysInfos():
    templ = "<div class='tile'><table>{}</table></div>"
    content = ""

    headerTempl = "<tr>" + "<th>{}</th>" * (len(data) + 1) + "</tr>"
    rowTempl = "<tr>" + "<td>{}</td>" * (len(data) + 1) + "</tr>"

    content += headerTempl.format("System Info", *data.keys())
    infos = data[data.keys()[0]]["Sysinfos"]
    for infoName in sorted(infos):
        res = []
        for fileName in sorted(data):
            res.append(data[fileName]["Sysinfos"][infoName])
        content += rowTempl.format(infoName, *res)
    return templ.format(content)


def loadDataForSingleBenchmark():
    """Loads a single benchmark"""
    data[opts.benchmarks] = loadJSONData(opts.benchmarks)


def loadDataForMultipleBenchmarks():
    """Loads a bunch of benchmarks."""
    for fileName in opts.benchmarks:
        data[fileName] = loadJSONData(fileName)
    areBenchmarksComparable(data)


def areBenchmarksComparable(benchmarks):
    """Checks the structure of each benchmark result. The same benchsuite is
    necessary for comparison. The benches and the arguments are therefore checked.

    :param benchmarks: list with all benchmarks
    :raises RuntimeError: if the strucutre of the benchmarks is unequal
    """

    # getAllBenches returns the benches of the first element
    f0Benches = getAllBenches()
    for fileName in benchmarks:
        fnBenches = getAllBenches(fileName).keys()
        if f0Benches.keys() != fnBenches:
            raise RuntimeError("Can not compare given benchmarks! Different benches.")
        for benchKey in fnBenches:
            if getBenchArgs(benchKey) != getBenchArgs(benchKey, fileName):
                raise RuntimeError("Can not compare given benchmarks! Different args in bench: %s" % benchKey)


def iterateBenches():
    """Iterates over each bench and calls a render function to display the data.
    The render functions will produce html code. This code will be put together and
    saved as .html file.
    """
    body = renderSysInfos()
    benches = getAllBenches()
    for benchKey in benches:
        logger.info("Render bench: " + benchKey)
        body += renderBench(benchKey)
    writeToFile(template.format(body), opts.outfile)


def renderBench(benchKey):
    """Generates html code of the given bench name to display its data.
    This function will display a heading, the arguments, table and diagramms.

    :param benchKey: the name of the benchmark
    :returns: string with html code
    """
    title = "<h2>{0}</h2>".format(benchKey)
    tileTempl = "<div class='tile'>{0}</div>"
    args = renderBenchArgs(benchKey)
    data = renderBenchData(benchKey)
    return tileTempl.format(title + args + data)


def renderBenchData(benchName):
    """Produces html code for the data of the given bench name.
    A diagramm and tables are created.

    :param benchName: name of the bench
    :returns: html code of the data
    """
    res = ""
    body = createDiagramm(benchName)
    body += renderTablesByTypes(benchName)
    return body


def getTestResult(fileName, benchName, benchTest):
    """Helper function to return the result of a bench test.

    :param fileName: name of the file
    :param benchName: name of the benchmark
    :param benchTest: name of the test
    :returns: the selected data from specified file name
    """
    return getAllBenches(fileName)[benchName]["data"][benchTest]


def getAllBenches(fileName=""):
    """Helper function to return all benchmarks. If no file name is applied the
    data is token from the first file.

    :param fileName: file where the information shall be taken from
    :returns: a dict of all benchmarks
    """
    if fileName == "":
        fileName = data.keys()[0]
    return data[fileName]["results"]


def getAllBenchTests(benchName):
    """Helper function to return all test of a benchmark.

    :param benchName: name of the benchmark
    :returns: a dict of all test of a benchmark
    """
    fileName = data.keys()[0]
    return getAllBenches(fileName)[benchName]['data']


def getBenchArgs(benchName, fileName=""):
    """Helper function to return the arguments of a benchmark.  If no file name
    is applied the data is token from the first file.

    :param benchName: name of the benchmark
    :param fileName: file where the information shall be taken from
    :returns: a dict of arguments
    """
    return getAllBenches(fileName)[benchName]["args"]


def createDiagramm(benchName):
    """Produce html js code to display the data of a benchmark as diagramm.
    The javascript function can be find in chart.js.

    :param benchName: name of the benchmark
    :returns: html/js code of the diagramm.
    """
    elementTempl = """
    <div id="{0}">
        <script>
            var data = {1};
            createBarChart("#{0}",data);
        </script>
     </div>"""
    tableContent = []
    for (benchTestName, content) in getAllBenchTests(benchName).iteritems():
        for fileName in data:
            val = getTestResult(fileName, benchName, benchTestName)["value"]
            if content["type"] == "time_series":
                timeList = content["value"]
                sumTime = sum(timeList)
                avg = sumTime / len(timeList)
                val = avg
            tableContent.append({"file": fileName, "name": benchTestName.encode('UTF-8'), "value": val})
    return elementTempl.format(benchTestName, tableContent)


def renderTablesByTypes(benchName):
    """Creates tables for each type of bench test.

    :param benchName: name of the benchmark
    :return: the html code
    """
    types = ["time", "time_series"]
    res = ""
    for t in types:
        res += renderTableByType(benchName, t)
    return res


def renderTableByType(benchName, type):
    """Creates a table of specific type of bench tests.

    :param benchName: name of the benchmark
    :param type: type of the benchmark (e.g. 'time', 'time_series')
    :returns: html code of the table.
    """
    header = "<h4>Tabelle {}</h4>".format(type)
    elements = dict((benchTestName, content) for (benchTestName, content) in getAllBenchTests(benchName).iteritems() if content["type"] == type)
    if len(elements) == 0:
        return ""

    content = "<table>"
    if type == "time_series":
        content += renderTimeSeriesRows(benchName, elements)
    elif type == "time":
        content += renderTimeRows(benchName, elements)

    content += "</table>"
    return header + content


def renderTimeRows(benchName, elements):
    """Creates the rows for the table. Each row display data of type 'time'.
    The elements parameter contains a dict which is already filtered by this type.

    :param benchName: name of the benchmark
    :param elements: filtered dict which is containing test
    :returns: string containing the rows
    """
    content = ""

    headerTempl = "<tr>" + "<th>{}</th>" * (len(data) + 1) + "</tr>"
    rowTempl = "<tr>" + "<td>{}</td>" * (len(data) + 1) + "</tr>"

    content += headerTempl.format("Test", *data.keys())
    for benchTestName in sorted(elements):
        res = []
        for fileName in sorted(data):
            res.append(getTestResult(fileName, benchName, benchTestName)["value"])
        content += rowTempl.format(benchTestName, *res)
    return content


def renderTimeSeriesRows(benchName, elements):
    """Creates the rows for the table. Each row display data of type 'time_series'.
    The elements parameter contains a dict which is already filtered by this type.

    :param benchName: name of the benchmark
    :param elements: filtered dict which is containing test
    :returns: string containing the rows
    """
    content = ""

    headerTempl = "<tr>" + "<th>{}</th>" * (len(data) + 2) + "</tr>"
    outerRowTempl = "<tr><td>{}</td><td colspan='{}'><table>{}</table></td></tr>"
    innerRowTempl = "<tr>" + "<td>{}</td>" * (len(data) + 1) + "</tr>"

    content += headerTempl.format("Test", "Aggregation", *data.keys())
    for benchTestName in sorted(elements):
        innerContent = ""
        resMax = []
        resMin = []
        resSum = []
        resAvg = []
        for fileName in sorted(data):
            timeList = getTestResult(fileName, benchName, benchTestName)["value"]
            maxVal = max(timeList)
            minVal = min(timeList)
            sumVal = sum(timeList)
            avgVal = sumVal / len(timeList)
            resMax.append(maxVal)
            resMin.append(minVal)
            resSum.append(sumVal)
            resAvg.append(avgVal)
        innerContent += innerRowTempl.format("Max", *resMax)
        innerContent += innerRowTempl.format("Min", *resMin)
        innerContent += innerRowTempl.format("Sum", *resSum)
        innerContent += innerRowTempl.format("Average", *resAvg)
        content += outerRowTempl.format(benchTestName, (len(data) + 1), innerContent)
    return content


def renderTextByType(content):
    """Produce html code to display the given data as text.

    :param content: data which shall be shown.
    :returns: html code
    """
    res = "<h4>{}</h4>".format(content["type"])
    dlTempl = """
        <dl>
        {0}
       </dl>
    """
    dlInnerTempl = "<dt>{0}</dt><dd>{1}</dd>"
    if content["type"] == "time_series":
        timeList = content["value"]
        lenTimeList = len(timeList)
        if lenTimeList > 0:
            maxVal = max(timeList)
            minVal = min(timeList)
            minVal = sum(timeList)
            avgVal = minVal / len(timeList)
            dlInner = ""
            dlInner += dlInnerTempl.format("Unit:", content["unit"])
            dlInner += dlInnerTempl.format("Max:", maxVal)
            dlInner += dlInnerTempl.format("Min:", minVal)
            dlInner += dlInnerTempl.format("Sum:", minVal)
            if "totalTime" in content:
                dlInner += dlInnerTempl.format("Total Time:", content["totalTime"])
            dlInner += dlInnerTempl.format("Average:", avgVal)
            res += dlTempl.format(dlInner)
    if content["type"] == "time":
        dlInner = ""
        dlInner += dlInnerTempl.format("Result:", str(content["value"]) + " " + content["unit"])
        res += dlTempl.format(dlInner)
    return res


def renderBenchArgs(benchName):
    """Displays the arguments of a benchmark in a table.

    :param benchName: name of the benchmark
    :returns: html table with arguments of the given bench
    """
    result = """
        <table>
            <tr>
                <th>Argument</th>
                <th>Value</th>
            </tr>
            {0}
        </table>
    """
    args = getBenchArgs(benchName)
    rows = ""
    for key, val in sorted(args.iteritems()):
        rows = rows + "\n<tr><td>{0}</td><td>{1}</td></tr>".format(key, val)
    result = result.format(rows)
    return result


def loadJSONData(file):
    """This functions load the json-data from a file.

    :param file: name of the input file
    :returns: json data
    """
    try:
        with open(file) as dataFile:
            data = json.load(dataFile)
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


def writeToFile(data, outfile):
    """This functions dumps json data into a file.

    :param data: json data
    :param outfile: name of the output file
    """
    outfile = os.path.join(currentPath, "html", outfile)
    logger.info("Saving Results to file: " + outfile)
    try:
        with open(outfile, 'w') as out:
            out.write(data)
    except IOError as err:
        logger.error("Could not open file to save the data! " + str(err))
    except:
        logger.error("Unexpected error occurred! " + str(sys.exc_info()[0:1]))
    else:
        logger.info("Saving successful")

if __name__ == "__main__":
    # CLI
    parser = argparse.ArgumentParser(description="""Reads benchmark data from a json file to display the data in human readable output.
                                    Each benchmark will therefore be rendered to display its results as a html file.""")
    parser.add_argument("--benchmarks", "-s", nargs='+', default=benchmarkFile, help="One or more json files which contain the benchmarks.")
    parser.add_argument("--outfile", "-o", nargs='?', default=outputFile, help="The results will be stored in this file.")

    # Grab the opts from argv
    opts = parser.parse_args()
    main()
